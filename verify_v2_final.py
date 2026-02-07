from blockchain import Blockchain, Block
from wallet import Transaction
from consensus import ProofOfWork
import os
import math
import time

def test_sraw_final():
    print("--- Phase 1: Setup Multi-Miner Economy (Satoshis) ---")
    db = 'chain_v2.db'
    if os.path.exists(db): os.remove(db)
    
    bc = Blockchain()
    
    # Simulate 3 Miners with different activity levels
    # Miner 1 will find the block
    print("[*] Recording Activity...")
    for _ in range(100): bc.record_activity("M1")
    for _ in range(25): bc.record_activity("M2")
    for _ in range(4): bc.record_activity("M3")
    
    # --- PHASE 2: EMULATE NODE.PY GET-WORK ---
    print("--- Phase 2: Emulating get-work (Pre-calculating Job) ---")
    last_block = bc.get_last_block()
    index = last_block.index + 1
    
    # Calculate Rewards exactly like node.py
    total_reward = bc.get_reward_for_block(index) # 10,000 $HOME
    total_fees = 0 # No txs in this test
    winner_reward_base = total_reward // 2
    community_pool = total_reward - winner_reward_base
    
    rewards = []
    rewards.append(Transaction("SYSTEM", "M1", winner_reward_base + total_fees, fee=0, data={"type":"reward_winner"}))
    
    active_miners = bc.get_active_miners(limit=100)
    weights = {addr: math.sqrt(count) for addr, count in active_miners.items()}
    total_weight = sum(weights.values())
    
    for addr, weight in weights.items():
        share = int((weight / total_weight) * community_pool)
        if share > 0:
            rewards.append(Transaction("SYSTEM", addr, share, {"type":"reward_community"}))

    # Calculate Merkle Root
    merkle_root = ProofOfWork.calculate_merkle_root([r.to_dict() for r in rewards])
    
    # Store Job
    bc.add_mining_job(merkle_root, [], rewards)
    print(f"[*] Job Cached. Merkle Root: {merkle_root[:10]}...")

    # --- PHASE 3: MINING & SUBMISSION ---
    print("--- Phase 3: Mining & Submission ---")
    ts = time.time()
    nonce, h = ProofOfWork.mine(index, last_block.hash, ts, merkle_root, "M1", bc.target)
    
    submission = {
        "index": index,
        "previous_hash": last_block.hash,
        "timestamp": ts,
        "merkle_root": merkle_root,
        "validator": "M1",
        "nonce": nonce,
        "hash": h
    }
    
    success = bc.submit_block(submission)
    
    if success:
        print("[+] Block Accepted!")
        bal1 = bc.get_balance("M1") / 10**8
        bal2 = bc.get_balance("M2") / 10**8
        bal3 = bc.get_balance("M3") / 10**8
        
        print(f"[*] M1 (Winner+Share) Balance: {bal1} $HOME")
        print(f"[*] M2 (Active Share) Balance: {bal2} $HOME")
        print(f"[*] M3 (Light Share) Balance: {bal3} $HOME")
        
        # M1 = 5000 (win) + (10/17)*5000 (~2941) = ~7941
        # M2 = (5/17)*5000 = ~1470
        # M3 = (2/17)*5000 = ~588
        
        if bal1 > 7000 and bal2 > 1000 and bal3 > 500:
            print("\n[SUCCESS] V2 SRAW POOL ENGINE FULLY VERIFIED!")
            print("Winner and active community miners received proportional rewards.")
        else:
            print("\n[FAILURE] Math verify failed.")
    else:
        print("\n[FAILURE] Block Rejected.")

if __name__ == "__main__":
    test_sraw_final()
