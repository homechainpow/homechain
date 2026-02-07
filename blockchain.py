import hashlib
import json
import time
import os
import math
import random
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
PRUNING_WINDOW = 30 * 86400 # 30 Days (Default)
POLL_COOLDOWN = 10         # 10s between shares for same address

class Block:
    def __init__(self, index: int, valid_transactions: List[Transaction], previous_hash: str, validator: str, timestamp: float = None, nonce: int = 0, target: int = None, rewards: List[Transaction] = None, hash: str = None):
# ... (rest of Block class is fine, just re-declaring to keep context for replace)
        self.index = index
        self.timestamp = timestamp or time.time()
        self.transactions = valid_transactions
        self.rewards = rewards or [] 
        self.previous_hash = previous_hash
        self.validator = validator
        self.nonce = nonce
        self.target = target or ProofOfWork.MAX_TARGET
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.compute_hash()

    def calculate_merkle_root(self) -> str:
        """Helper to get merkle root from block transactions + rewards."""
        all_txs = [tx.to_dict() for tx in self.transactions] + [tx.to_dict() for tx in self.rewards]
        return ProofOfWork.calculate_merkle_root(all_txs)

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "rewards": [tx.to_dict() for tx in self.rewards],
            "merkle_root": self.merkle_root,
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
        return ProofOfWork.calculate_hash(
            self.index, self.previous_hash, self.timestamp, self.merkle_root, self.validator, self.nonce
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
        self.mining_jobs = {} # V2 Catch: {merkle_root: (transactions, rewards)}
        self.used_jobs = set() # Prevent job reuse
        self.poll_rate_cache = {} # {address: last_poll_time}
        
        # Note: Multi-mining is allowed by default in production.
        
        if not self.load_chain():
            self.create_genesis_block()
        else:
            self.load_queue()
            self.target = self.adjust_difficulty()

    def add_mining_job(self, merkle_root: str, txs: list, rewards: list):
        """Cache a mining job for later submission verification."""
        # Limit cache size to 1000 jobs
        if len(self.mining_jobs) > 1000:
            # Pop the first item (oldest)
            first_key = next(iter(self.mining_jobs))
            self.mining_jobs.pop(first_key)
        self.mining_jobs[merkle_root] = (txs, rewards)

    def get_median_time_past(self) -> float:
        """Calculate the median timestamp of the last 11 blocks."""
        if not self.chain: return 0
        last_blocks = self.chain[-11:]
        timestamps = sorted([b.timestamp for b in last_blocks])
        return timestamps[len(timestamps) // 2]

    def create_genesis_block(self):
        # Pre-mine 1B coins to SYSTEM for initial airdrops/tests
        PREMINE = 1_000_000_000 * COIN
        genesis_tx = Transaction("SYSTEM", "GENESIS", PREMINE, 0, {"message": "HomeChain V2 Genesis - Optimized Mesin"})
        
        # Calculate Merkle Root for Genesis
        merkle_root = ProofOfWork.calculate_merkle_root([genesis_tx.to_dict()])
        
        # Genesis starts at MAX_TARGET
        nonce, hash_val = ProofOfWork.mine(0, "0", 1700000000, merkle_root, "SYSTEM", ProofOfWork.MAX_TARGET)
        
        genesis_block = Block(0, [genesis_tx], "0", "SYSTEM", timestamp=1700000000, nonce=nonce, target=ProofOfWork.MAX_TARGET)
        genesis_block.hash = hash_val
        
        self.chain.append(genesis_block)
        if not hasattr(self, 'conn'): self._init_db()
        self.update_state(genesis_block) # PRESERVE PREMINE IN SQLite
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
            reward = reward // 2
            
        return reward

    def calculate_merkle_root(self, block: Block) -> str:
        """
        Helper to get merkle root from block transactions + rewards.
        """
        all_txs = [tx.to_dict() for tx in block.transactions] + [tx.to_dict() for tx in block.rewards]
        return ProofOfWork.calculate_merkle_root(all_txs)

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
        Refactored: Uses Job Cache for V2 Merkle efficiency.
        """
        merkle_root = block_data.get('merkle_root')
        if not merkle_root or merkle_root not in self.mining_jobs:
            print(f"[!] Block submission failed: Merkle Root {merkle_root} not in job cache.")
            return False
            
        if merkle_root in self.used_jobs:
            print("[!] Block submission failed: Merkle Root already used.")
            return False
        
        txs, rewards = self.mining_jobs[merkle_root]
        
        last_block = self.get_last_block()
        if block_data['previous_hash'] != last_block.hash:
            return False # Stale block
        
        # Construct V2 Block (avoiding double compute_hash logic)
        new_block = Block(
            index=block_data['index'],
            valid_transactions=txs,
            previous_hash=block_data['previous_hash'],
            validator=block_data['validator'],
            timestamp=block_data['timestamp'],
            nonce=block_data['nonce'],
            target=self.target,
            rewards=rewards,
            hash=block_data['hash']
        )
        
        # 1. Verify PoW
        if not ProofOfWork.is_valid_proof(new_block.hash, self.target):
            print(f"Invalid PoW: {new_block.hash} >= {self.target}")
            return False
            
        # 2. Verify Block Integrity & Timestamp (MTP)
        if new_block.calculate_merkle_root() != merkle_root:
            print("[!] Merkle Root mismatch!")
            return False

        if new_block.timestamp <= self.get_median_time_past():
            print("[!] Block rejected: Timestamp is before Median Time Past (MTP).")
            return False
            
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
        total_fees = sum(tx.fee for tx in new_block.transactions)
        
        winner_reward_base = total_reward // 2 # 50% Winner
        community_pool = total_reward - winner_reward_base # 50% Community
        
        # Winner Portion (Base + Fees)
        winner_rtx = Transaction("SYSTEM", new_block.validator, winner_reward_base + total_fees, fee=0, data={"type": "reward_winner", "fees": total_fees})
        new_block.rewards.append(winner_rtx)
        
        # 2. SRAW (Square-Root Activity Weight) Distribution
        active_miners = self.get_active_miners(limit=100)
        if active_miners:
            # Calculate Weights: sqrt(poll_count)
            weights = {addr: math.sqrt(count) for addr, count in active_miners.items()}
            total_weight = sum(weights.values())
            
            if total_weight > 0:
                for addr, weight in weights.items():
                    share = int((weight / total_weight) * community_pool)
                    if share > 0:
                        bonus_rtx = Transaction("SYSTEM", addr, share, {"type": "reward_community", "weight": round(weight, 2)})
                        new_block.rewards.append(bonus_rtx)
            
            # Clear only very old activity, keep the rolling window healthy
            self.cursor.execute("DELETE FROM miner_activity WHERE last_poll < ?", (time.time() - 86400,))
        else:
            # Fallback: if no active miners, remaining goes to winner
            winner_rtx.amount += community_pool

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
        self.used_jobs.add(merkle_root)
        
        # Prevent used_jobs from growing indefinitely
        if len(self.used_jobs) > 1000:
            # Simple way to pop oldest from a set (not ordered, but works for cache)
            self.used_jobs.pop()
        
        # Update State / Pending Txs
        block_tx_signatures = set()
        for tx in new_block.transactions:
            if tx.signature:
                block_tx_signatures.add(tx.signature)
        
        self.pending_transactions = [tx for tx in self.pending_transactions if tx.signature not in block_tx_signatures]
        
        for tx in new_block.transactions:
            self.vm.execute(tx)
        for rtx in new_block.rewards:
            self.vm.execute(rtx)
        
        # Update Fast State (V2 SQLite)
        self.update_state(new_block)
            
        # Adjust difficulty for next block
        self.target = self.adjust_difficulty()
        self.save_chain()
        return True

    def adjust_difficulty(self) -> int:
        """
        V2 Optimized SMA: Average of last 144 blocks (~2.4 hours).
        Ensures smooth transitions and stability.
        """
        WINDOW = 144
        if len(self.chain) < WINDOW:
            # Fallback to simple proportional if chain is short
            if len(self.chain) < 2: return ProofOfWork.MAX_TARGET
            last = self.chain[-1]
            prev = self.chain[-2]
            actual = max(1, last.timestamp - prev.timestamp)
            ratio = actual / 60.0
            new_target = int(self.target * ratio)
            return min(ProofOfWork.MAX_TARGET, max(1, new_target))

        # Calculate average block time over WINDOW
        relevant_blocks = self.chain[-WINDOW:]
        total_time = relevant_blocks[-1].timestamp - relevant_blocks[0].timestamp
        avg_time = total_time / (WINDOW - 1)
        
        # Adjust proportionally
        ratio = avg_time / 60.0
        # Dampen adjustment to max 10% change per block for stability
        ratio = max(0.9, min(1.1, ratio))
        
        new_target = int(self.target * ratio)
        return min(ProofOfWork.MAX_TARGET, max(1, new_target))

    def get_pending_txs(self):
        # Limit to 500 transactions per block to keep hashing light on 5 vCPUs
        return [tx.to_dict() for tx in self.pending_transactions[:500]]

    def get_balance(self, address: str) -> int:
        """O(1) look-up from SQLite state table."""
        try:
            if not hasattr(self, 'conn') or self.conn is None: self._init_db()
            self.cursor.execute("SELECT balance FROM balances WHERE address=?", (address,))
            row = self.cursor.fetchone()
            return int(row[0]) if row else 0
        except:
            return 0

    def rebuild_state(self):
        """No longer used in V2 as state is in SQLite."""
        pass

    def update_state(self, block: Block):
        """Atomically update SQLite balances."""
        if not hasattr(self, 'conn') or self.conn is None: self._init_db()
        
        # 1. Process Transactions
        for tx in block.transactions:
            if tx.sender != "SYSTEM":
                sender_bal = int(self.get_balance(tx.sender)) - (int(tx.amount) + int(tx.fee))
                self.cursor.execute("REPLACE INTO balances (address, balance) VALUES (?, ?)", (tx.sender, sender_bal))
            
            recv_bal = int(self.get_balance(tx.receiver)) + int(tx.amount)
            self.cursor.execute("REPLACE INTO balances (address, balance) VALUES (?, ?)", (tx.receiver, recv_bal))
        
        # 2. Process Rewards
        for rtx in block.rewards:
            recv_bal = int(self.get_balance(rtx.receiver)) + int(rtx.amount)
            self.cursor.execute("REPLACE INTO balances (address, balance) VALUES (?, ?)", (rtx.receiver, recv_bal))
        
        self.conn.commit()

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

    def record_activity(self, address: str):
        """PPLNS: Track shares with rate limiting."""
        if address == "SYSTEM": return
        
        now = time.time()
        # 1. Rate Limiting (Prevent Share Inflation Spam)
        last_time = self.poll_rate_cache.get(address, 0)
        if now - last_time < POLL_COOLDOWN:
            return False # Rejecting too frequent polls
            
        self.poll_rate_cache[address] = now
        
        if not hasattr(self, 'conn') or self.conn is None: self._init_db()
        # 1. Update basic last_poll for UI/Explorer
        self.cursor.execute("""
            INSERT INTO miner_activity (address, last_poll, poll_count) 
            VALUES (?, ?, 1)
            ON CONFLICT(address) DO UPDATE SET 
                poll_count = poll_count + 1,
                last_poll = ?
        """, (address, now, now))
        
        # 2. Add as a 'Share' for PPLNS distribution
        self.cursor.execute("INSERT INTO miner_shares (address, timestamp) VALUES (?, ?)", (address, now))
        
        # Periodic Share Cleanup (Keep only last 5000 to save space)
        if random.random() < 0.01: # 1% chance per poll to prune
            self.prune_shares()
            
        self.conn.commit()

    def get_active_miners(self, limit=100) -> dict:
        """PPLNS: Calculate weights from the last 1000 network-wide shares."""
        if not hasattr(self, 'conn') or self.conn is None: self._init_db()
        # Get the 'Last N Shares' (Industrial standard)
        WINDOW_SIZE = 1000
        self.cursor.execute("""
            SELECT address, COUNT(*) as share_count FROM (
                SELECT address FROM miner_shares 
                ORDER BY id DESC LIMIT ?
            ) GROUP BY address ORDER BY share_count DESC LIMIT ?
        """, (WINDOW_SIZE, limit))
        return {row[0]: row[1] for row in self.cursor.fetchall()}

    def prune_shares(self):
        """Keep only the last 5000 shares to prevent DB bloat."""
        self.cursor.execute("""
            DELETE FROM miner_shares WHERE id NOT IN (
                SELECT id FROM miner_shares ORDER BY id DESC LIMIT 5000
            )
        """)

    # [DATABASE MIGRATION: SQLite]
    def _init_db(self):
        import sqlite3
        self.conn = sqlite3.connect('chain_v2.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        # V2 Tables
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS blocks
                               (idx INTEGER PRIMARY KEY, hash TEXT, prev_hash TEXT, data TEXT, timestamp REAL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS state_vars
                               (key TEXT PRIMARY KEY, value TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS balances
                               (address TEXT PRIMARY KEY, balance INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS miner_activity
                               (address TEXT PRIMARY KEY, last_poll REAL, poll_count INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS miner_shares
                               (id INTEGER PRIMARY KEY AUTOINCREMENT, address TEXT, timestamp REAL)''')
        self.cursor.execute('''CREATE INDEX IF NOT EXISTS idx_balances_addr ON balances(address)''')
        self.cursor.execute('''CREATE INDEX IF NOT EXISTS idx_shares_id ON miner_shares(id DESC)''')
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
        
        # Periodic Pruning (Every 100 blocks)
        if last_block.index % 100 == 0:
            self.prune_history()
            
        self.conn.commit()

    def prune_history(self):
        """Delete old blocks to save space. State is preserved in balances table."""
        if not hasattr(self, 'conn') or self.conn is None: self._init_db()
        cutoff = time.time() - PRUNING_WINDOW
        # Keep at least the SMA window (144 blocks) regardless of time
        min_idx = len(self.chain) - 150
        if min_idx < 0: min_idx = 0
        
        self.cursor.execute("DELETE FROM blocks WHERE timestamp < ? AND idx < ?", (cutoff, min_idx))
        print(f"[*] Pruned old blocks before timestamp {cutoff}")

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

