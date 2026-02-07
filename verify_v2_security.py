from blockchain import Blockchain, Block, POLL_COOLDOWN
from consensus import ProofOfWork
from wallet import Transaction
import os
import time
import math

def test_security_hardening():
    print("--- Phase 1: Rate Limit Test (Anti-Spam) ---")
    db = 'chain_v2_security.db'
    if os.path.exists(db): os.remove(db)
    
    bc = Blockchain()
    # Mocking DB connection for this specific test file
    import sqlite3
    bc.conn = sqlite3.connect(db, check_same_thread=False)
    bc.cursor = bc.conn.cursor()
    bc._init_db()

    addr = "M1"
    res1 = bc.record_activity(addr)
    res2 = bc.record_activity(addr) # Immediate second poll
    
    if res2 is False:
        print(f"[SUCCESS] Rate Limit active. Second poll blocked within {POLL_COOLDOWN}s.")
    else:
        print("[FAILURE] Rate Limit failed to block spam.")

    print("\n--- Phase 2: PPLNS Rolling Window Test ---")
    # Simulate 1200 polls from different miners to see if it limits to 1000
    print("[*] Simulating 1200 polls...")
    # Bypass cooldown for simulation speed by manually inserting
    now = time.time()
    for i in range(1200):
        m_addr = f"S_{i}"
        bc.cursor.execute("INSERT INTO miner_shares (address, timestamp) VALUES (?, ?)", (m_addr, now))
    bc.conn.commit()
    
    active = bc.get_active_miners(limit=200)
    print(f"[*] Active miners in snapshot: {len(active)}")
    if len(active) <= 100: # get_active_miners has a limit=100 default/parameter
        print("[SUCCESS] Distribution limited to Top 100 active miners.")
    
    print("\n--- Phase 3: MTP (Median Time Past) Test ---")
    bc.create_genesis_block()
    last = bc.get_last_block()
    
    # Try to submit a block with a timestamp in the past
    bad_ts = last.timestamp - 1000
    nb_bad = {
        "index": 1,
        "previous_hash": last.hash,
        "timestamp": bad_ts,
        "merkle_root": "0"*64,
        "validator": "M1",
        "nonce": 0,
        "hash": "0"*64
    }
    # We need to add the job to bypass the cache check but MTP should still fail it
    bc.add_mining_job("0"*64, [], [])
    
    if bc.submit_block(nb_bad) is False:
        print("[SUCCESS] MTP blocked block with past timestamp.")
    else:
        print("[FAILURE] MTP allowed old timestamp.")

    print("\n--- Phase 4: Job Reuse Test ---")
    # Mine a valid block 1
    ts = time.time()
    rewards = [Transaction("SYSTEM", "M1", 5000, 0)]
    merkle = ProofOfWork.calculate_merkle_root([r.to_dict() for r in rewards])
    bc.add_mining_job(merkle, [], rewards)
    
    nonce, h = ProofOfWork.mine(1, last.hash, ts, merkle, "M1", bc.target)
    good_block = {
        "index": 1, "previous_hash": last.hash, "timestamp": ts,
        "merkle_root": merkle, "validator": "M1", "nonce": nonce, "hash": h
    }
    
    bc.submit_block(good_block) # Success 1
    if bc.submit_block(good_block) is False:
        print("[SUCCESS] Job Reuse blocked. Cannot commit same solution twice.")
    else:
        print("[FAILURE] Job Reuse permitted.")

if __name__ == "__main__":
    test_security_hardening()
