import hashlib
import json
import time
import os
import math
from typing import List
from wallet import Transaction
from consensus import ProofOfWork
from vm import VirtualMachine

CHAIN_FILE = "chain_data.json"

# Supply & Halving Constants (INTEGER PRECISION - SATOSHIS)
COIN = 100_000_000
MAX_SUPPLY = 21_000_000_000 * COIN
INITIAL_REWARD = 10_000 * COIN
ERA_1_BLOCKS = 14_400  # 10 Days at 60s/block
MIN_FEE = 1_000_000    # 0.01 HOME

class Block:
    def __init__(self, index: int, valid_transactions: List[Transaction], previous_hash: str, validator: str, timestamp: float = None, nonce: int = 0, target: int = None, rewards: List[Transaction] = None):
# ... (rest of Block class is fine, just re-declaring to keep context for replace)
        self.index = index
        self.timestamp = timestamp or time.time()
        self.transactions = valid_transactions
        self.rewards = rewards or [] 
        self.previous_hash = previous_hash
        self.validator = validator
        self.nonce = nonce
        self.target = target or ProofOfWork.MAX_TARGET
        self.hash = self.compute_hash()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "rewards": [tx.to_dict() for tx in self.rewards],
            "previous_hash": self.previous_hash,
            "validator": self.validator,
            "nonce": self.nonce,
            "target": self.target,
            "hash": self.hash
        }
    
    @classmethod
    def from_dict(cls, data):
        reconstructed_txs = []
        for tx_data in data['transactions']:
            if isinstance(tx_data, dict):
                tx = Transaction(
                    sender=tx_data['sender'],
                    receiver=tx_data['receiver'],
                    amount=int(tx_data['amount']),
                    fee=int(tx_data.get('fee', 0)),
                    data=tx_data.get('data'),
                    signature=tx_data.get('signature'),
                    timestamp=tx_data.get('timestamp')
                )
                reconstructed_txs.append(tx)
            else:
                reconstructed_txs.append(tx_data)

        reconstructed_rewards = []
        if 'rewards' in data:
            for r_data in data['rewards']:
                rtx = Transaction(
                    sender=r_data['sender'],
                    receiver=r_data['receiver'],
                    amount=int(r_data['amount']), 
                    data=r_data.get('data'),
                    timestamp=r_data.get('timestamp')
                )
                reconstructed_rewards.append(rtx)
        
        return cls(
            index=data['index'],
            valid_transactions=reconstructed_txs,
            previous_hash=data['previous_hash'],
            validator=data['validator'],
            timestamp=data['timestamp'],
            nonce=data.get('nonce', 0),
            target=data.get('target', ProofOfWork.MAX_TARGET),
            rewards=reconstructed_rewards
        )

    def compute_hash(self) -> str:
        tx_str = json.dumps([tx.to_dict() for tx in self.transactions], sort_keys=True)
        return ProofOfWork.calculate_hash(
            self.index, self.previous_hash, self.timestamp, tx_str, self.validator, self.nonce
        )

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.vm = VirtualMachine()
        self.nodes = set()
        self.target = ProofOfWork.MAX_TARGET
        self.validators = [] # Track all unique validators
        self.reward_queue = [] # Queue for bonus distribution
        self.device_map = {} # Anti-Sybil: {device_id: address}
        self.balances = {}   # State DB: {address: balance}
        
        # Note: Multi-mining is allowed by default in production.
        
        if not self.load_chain():
            self.create_genesis_block()
        else:
            self.rebuild_state()
            self.load_queue()
            self.target = self.adjust_difficulty()

    def create_genesis_block(self):
        genesis_tx = Transaction("SYSTEM", "GENESIS", 0, {"message": "HomeChain Proportional DDA Era (V2 Integer)"})
        # Genesis starts at MAX_TARGET
        nonce, hash_val = ProofOfWork.mine(0, "0", 1700000000, json.dumps([genesis_tx.to_dict()], sort_keys=True), "SYSTEM", ProofOfWork.MAX_TARGET)
        
        genesis_block = Block(0, [genesis_tx], "0", "SYSTEM", timestamp=1700000000, nonce=nonce, target=ProofOfWork.MAX_TARGET)
        genesis_block.hash = hash_val
        
        self.chain.append(genesis_block)
        self.save_chain()

    def rebuild_state(self):
        self.vm = VirtualMachine()
        self.validators = []
        seen = set()
        for block in self.chain:
            v = block.validator
            if v != "SYSTEM" and v not in seen:
                self.validators.append(v)
                seen.add(v)
            
            for tx in block.transactions:
                self.vm.execute(tx)
            
            for rtx in block.rewards:
                self.vm.execute(rtx)
        
        self.reward_queue = list(self.validators)

    def get_last_block(self) -> Block:
        return self.chain[-1]
        
    def get_reward_for_block(self, index) -> int:
        """
        Calculates Geometric Halving Reward (Integer).
        """
        if index == 0: return 0
        
        current_era_length = ERA_1_BLOCKS
        reward = INITIAL_REWARD
        era_end = current_era_length
        
        while index > era_end:
            current_era_length *= 2
            era_end += current_era_length
            reward = reward // 2 # Integer Division
            
        return reward

    def get_total_supply(self) -> int:
        supply = 0
        for b in self.chain:
            supply += self.get_reward_for_block(b.index)
        return min(supply, MAX_SUPPLY)

    def add_transaction(self, transaction: Transaction) -> bool:
        if transaction.is_valid():
            # Mandatory Fee Check
            if transaction.fee < MIN_FEE and transaction.sender != "SYSTEM":
                return False
            
            balance = self.get_balance(transaction.sender)
            if balance < (transaction.amount + transaction.fee) and transaction.sender != "SYSTEM":
                return False
            self.pending_transactions.append(transaction)
            return True
        return False

    def validate_transaction(self, tx: Transaction) -> bool:
        """Validate transaction without side effects."""
        if not tx.is_valid():
            return False
        if tx.sender != "SYSTEM":
            if tx.fee < MIN_FEE: return False
            if self.get_balance(tx.sender) < (tx.amount + tx.fee): return False
        return True

    def submit_block(self, block_data: dict) -> bool:
        """
        External miner submits a block.
        Refactored: Validate logic BEFORE append.
        """
        last_block = self.get_last_block()
        if block_data['previous_hash'] != last_block.hash:
            return False # Stale block
        
        new_block = Block.from_dict(block_data)
        
        # Verify PoW
        if not ProofOfWork.is_valid_proof(new_block.hash, self.target):
            print(f"Invalid PoW: {new_block.hash} >= {self.target}")
            return False
            
        # Verify Block Index
        if new_block.index != last_block.index + 1:
            return False

        # [CRITICAL LOGIC FIX]
        # Validate transactions by Dry-Running them on current state.
        # Ideally we clone the VM, but for prototype v2 we just check balances.
        # Since VM execute updates state in-place, we must be careful.
        # Better approach: We trust vm.execute to raise/return error, but we do it 
        # BEFORE self.chain.append.
        
        # We need a rollback mechanism or temporary state. 
        # For simplicity in this non-DB version, we'll verify balances manually again
        # OR we rely on the fact that if this crashes, we haven't appended yet.
        
        # 1. Calculate Rewards (Integer)
        total_reward = self.get_reward_for_block(new_block.index)
        
        # Aggregate Fees from Transactions
        total_fees = sum(tx.fee for tx in new_block.transactions)
        
        finder_reward = (total_reward // 2) + total_fees
        bonus_pool = total_reward // 2
        
        # Finder Reward
        finder_rtx = Transaction("SYSTEM", new_block.validator, finder_reward, fee=0, data={"type": "reward_finder", "fees_collected": total_fees})
        new_block.rewards.append(finder_rtx)
        
        # Add finder to known validators if new
        if new_block.validator != "SYSTEM" and new_block.validator not in self.validators:
            self.validators.append(new_block.validator)
            self.reward_queue.append(new_block.validator)

        # 2. Bonus Distribution (Integer)
        potential = [v for v in self.reward_queue if v != new_block.validator]
        if potential:
            count = min(100, len(potential))
            recipients = potential[:count]
            if len(recipients) > 0:
                reward_per = bonus_pool // len(recipients)
                
                for r in recipients:
                    bonus_rtx = Transaction("SYSTEM", r, reward_per, {"type": "reward_bonus", "block": new_block.index})
                    new_block.rewards.append(bonus_rtx)
                    # Move to back of the master queue
                    if r in self.reward_queue:
                        self.reward_queue.remove(r)
                        self.reward_queue.append(r)

        # 3. Dry Run Execution
        # In a real DB, we'd start a transaction. 
        # Here, we assume if all transactions are valid balance-wise, we proceed.
        # (Simplified refactor for now to avoid massive architecture change to VM)
        for tx in new_block.transactions:
            if not self.validate_transaction(tx):
                print(f"Invalid transaction in block: {tx.to_dict()}")
                return False

        # 4. Append & Execute (Commit)
        self.chain.append(new_block)
        
        # Update State / Pending Txs
        # Only remove transactions that were actually included in the block
        block_tx_signatures = set()
        for tx in new_block.transactions:
            if tx.signature:
                block_tx_signatures.add(tx.signature)
        
        self.pending_transactions = [tx for tx in self.pending_transactions if tx.signature not in block_tx_signatures]
        
        for tx in new_block.transactions:
            self.vm.execute(tx)
        for rtx in new_block.rewards:
            self.vm.execute(rtx)
        
        # Update Fast State
        self.update_state(new_block)
            
        # Adjust difficulty for next block
        self.target = self.adjust_difficulty()
        self.save_chain()
        return True

    def adjust_difficulty(self) -> int:
        """
        Responsive DDA: Adjust target proportional to block time ratio.
        Target Time: 60s
        """
        if len(self.chain) < 2:
            return ProofOfWork.MAX_TARGET
            
        last_block = self.chain[-1]
        prev_block = self.chain[-2]
        
        actual_time = last_block.timestamp - prev_block.timestamp
        if actual_time < 0.1: actual_time = 0.1
        
        # New Target = Old Target * (Actual Time / 60)
        # 1. Calculate ratio
        ratio = actual_time / 60.0
        
        # 2. Limit adjustment for stability (max 4x or 0.25x per block)
        ratio = max(0.25, min(4.0, ratio))
        
        new_target = int(self.target * ratio)
        
        # 3. Constrain to MAX_TARGET
        if new_target > ProofOfWork.MAX_TARGET:
            new_target = ProofOfWork.MAX_TARGET
        if new_target < 1: 
            new_target = 1
            
        return new_target

    def get_pending_txs(self):
        return [tx.to_dict() for tx in self.pending_transactions]

    def get_balance(self, address: str) -> int:
        """Fast O(1) balance lookup from state."""
        return self.balances.get(address, 0)

    def rebuild_state(self):
        """Reconstruct balance state from the entire chain on startup."""
        print("[*] Rebuilding state balances from history...")
        self.balances = {}
        for block in self.chain:
            self.update_state(block)
        print(f"[*] State rebuilt. Total accounts: {len(self.balances)}")

    def update_state(self, block: Block):
        """Update balance state with transactions and rewards from a new block."""
        # 1. Process Transactions
        for tx in block.transactions:
            # Subtract (Amount + Fee) from sender
            if tx.sender != "SYSTEM":
                self.balances[tx.sender] = self.balances.get(tx.sender, 0) - (tx.amount + tx.fee)
            # Add Amount to receiver
            self.balances[tx.receiver] = self.balances.get(tx.receiver, 0) + tx.amount
        
        # 2. Process Rewards
        for rtx in block.rewards:
            self.balances[rtx.receiver] = self.balances.get(rtx.receiver, 0) + rtx.amount

    def register_node(self, address: str):
        """Register a new peer node."""
        if address and address not in self.nodes:
            self.nodes.add(address)
            # Persist nodes list
            if hasattr(self, 'conn'):
                nodes_data = json.dumps(list(self.nodes))
                self.cursor.execute("REPLACE INTO state_vars VALUES ('nodes_list', ?)", (nodes_data,))
                self.conn.commit()
            return True
        return False

    # [DATABASE MIGRATION: SQLite]
    def _init_db(self):
        import sqlite3
        self.conn = sqlite3.connect('chain_v2.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS blocks
                               (idx INTEGER PRIMARY KEY, hash TEXT, prev_hash TEXT, data TEXT, timestamp REAL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS state_vars
                               (key TEXT PRIMARY KEY, value TEXT)''')
        self.conn.commit()

    def save_chain(self):
        """
        Optimized: Only save the last block (Append Only).
        User responsible for DB integrity.
        """
        import json
        if not hasattr(self, 'conn'): self._init_db()
        
        if not self.chain: return

        last_block = self.chain[-1]
        
        # Check if exists
        self.cursor.execute("SELECT idx FROM blocks WHERE idx=?", (last_block.index,))
        if self.cursor.fetchone():
            return # Already saved
            
        data_json = json.dumps(last_block.to_dict())
        self.cursor.execute("INSERT INTO blocks VALUES (?, ?, ?, ?, ?)", 
                           (last_block.index, last_block.hash, last_block.previous_hash, data_json, last_block.timestamp))
        
        # Save Queue & Devices
        q_data = json.dumps({"queue": self.reward_queue, "devices": self.device_map})
        self.cursor.execute("REPLACE INTO state_vars VALUES ('queue_data', ?)", (q_data,))
        self.conn.commit()

    def load_queue(self):
        if not hasattr(self, 'conn'): self._init_db()
        try:
            self.cursor.execute("SELECT value FROM state_vars WHERE key='queue_data'")
            row = self.cursor.fetchone()
            if row:
                data = json.loads(row[0])
                self.reward_queue = data.get("queue", [])
                self.device_map = data.get("devices", {})
        except:
            pass

        try:
            self.cursor.execute("SELECT value FROM state_vars WHERE key='nodes_list'")
            row = self.cursor.fetchone()
            if row:
                self.nodes = set(json.loads(row[0]))
        except:
            pass

    def load_chain(self) -> bool:
        if not hasattr(self, 'conn'): self._init_db()
        self.cursor.execute("SELECT data FROM blocks ORDER BY idx ASC")
        rows = self.cursor.fetchall()
        if not rows:
            return False
            
        loaded_chain = []
        for row in rows:
            block_data = json.loads(row[0])
            block = Block.from_dict(block_data)
            loaded_chain.append(block)
            
        self.chain = loaded_chain
        return True

    def register_validator(self, address, device_id="unknown"):
        """
        Simplified Registration: 
        Allow multiple wallets from any device.
        """
        if address == "SYSTEM": return
        
        if address not in self.validators:
            self.validators.append(address)
            if address not in self.reward_queue:
                self.reward_queue.append(address)
            self.save_chain()

