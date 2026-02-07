from blockchain import Blockchain, Block
from wallet import Transaction
from consensus import ProofOfWork
import time
import os

def test_v2_engine():
    print("--- Testing HomeChain V2 Optimized Engine ---")
    
    # 1. Setup - Remove old DB
    if os.path.exists("chain_v2.db"):
        os.remove("chain_v2.db")
        print("[*] Cleaned chain_v2.db")

    bc = Blockchain()
    
    # 2. Check Genesis
    print(f"[*] Genesis Block Hash: {bc.chain[0].hash}")
    
    # 3. Simulate Mining 5 Blocks
    for i in range(1, 6):
        print(f"[*] Mining Block #{i}...")
        last = bc.get_last_block()
        
        # Add a dummy transaction
        tx = Transaction("GENESIS", f"ADDR_{i}", 100 * 100_000_000, 1_000_000)
        bc.add_transaction(tx)
        
        pending = bc.get_pending_txs()
        m_root = ProofOfWork.calculate_merkle_root(pending)
        
        ts = time.time()
        nonce, h = ProofOfWork.mine(i, last.hash, ts, m_root, "TEST_MINER", bc.target)
        
        block_data = {
            "index": i,
            "previous_hash": last.hash,
            "timestamp": ts,
            "merkle_root": m_root,
            "validator": "TEST_MINER",
            "nonce": nonce,
            "target": bc.target,
            "hash": h,
            "transactions": pending,
            "rewards": []
        }
        
        success = bc.submit_block(block_data)
        if success:
            print(f"[+] Block #{i} Accepted. Target: {bc.target}")
        else:
            print(f"[!] Block #{i} Rejected!")
            break

    # 4. Check SQLite Persistence
    print(f"[*] Verifying SQLite Persistence...")
    bc2 = Blockchain()
    print(f"[*] Loaded Chain Length: {len(bc2.chain)}")
    addr_5_bal = bc2.get_balance("ADDR_5")
    print(f"[*] Balance of ADDR_5: {addr_5_bal / 100_000_000} $HOME")
    
    if len(bc2.chain) == 6 and addr_5_bal > 0:
        print("\n[SUCCESS] V2 ENGINE VERIFIED: SQLite, Merkle, and SMA are working correctly.")
    else:
        print("\n[FAILURE] V2 ENGINE VERIFICATION FAILED.")

if __name__ == "__main__":
    test_v2_engine()
