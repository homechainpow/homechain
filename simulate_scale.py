from blockchain import Blockchain, Block
from consensus import ProofOfWork
from wallet import Transaction
import os
import math
import time
import sqlite3

def simulate_200_miners_fast():
    print("--- Phase 1: Setup 200 Miner Network (Fast) ---")
    db = 'chain_v2_scale.db'
    if os.path.exists(db): os.remove(db)
    
    bc = Blockchain()
    # Close default connection to ensure we use our scale DB
    bc.conn.close()
    
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    # Re-init tables in the new DB
    cursor.execute('CREATE TABLE IF NOT EXISTS balances (address TEXT PRIMARY KEY, balance INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS miner_activity (address TEXT PRIMARY KEY, last_poll REAL, poll_count INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS state_vars (key TEXT PRIMARY KEY, value TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS blocks (idx INTEGER PRIMARY KEY, hash TEXT, prev_hash TEXT, data TEXT, timestamp REAL)')
    conn.commit()

    # Re-inject connection into blockchain object
    bc.conn = conn
    bc.cursor = cursor

    print("[*] Recording activity for 200 unique miners (Batch Mode)...")
    now = time.time()
    # Bulk insert for speed
    activity_data = []
    for i in range(1, 201):
        addr = f"MINER_{i}"
        polls = 201 - i # M1: 200, M2: 199 ... M100: 101 ... M200: 1
        activity_data.append((addr, now, polls))
    
    cursor.executemany("INSERT INTO miner_activity (address, last_poll, poll_count) VALUES (?, ?, ?)", activity_data)
    conn.commit()
    
    print("[*] Activity recorded. Generating Block...")

    # --- PHASE 2: BLOCK GENERATION ---
    bc.create_genesis_block()
    last_block = bc.get_last_block()
    index = last_block.index + 1
    winner = "MINER_1"
    
    total_reward = bc.get_reward_for_block(index)
    winner_reward_base = total_reward // 2
    community_pool = total_reward - winner_reward_base
    
    rewards = []
    rewards.append(Transaction("SYSTEM", winner, winner_reward_base, fee=0, data={"type":"win"}))
    
    active_miners = bc.get_active_miners(limit=100)
    print(f"[*] Community Pool Distribution (Code Limit: 100 miners)")
    
    weights = {addr: math.sqrt(count) for addr, count in active_miners.items()}
    total_weight = sum(weights.values())
    
    for addr, weight in weights.items():
        share = int((weight / total_weight) * community_pool)
        if share > 0:
            rewards.append(Transaction("SYSTEM", addr, share, {"type":"comm"}))

    print(f"[*] Total Reward Transactions created: {len(rewards)}")
    
    all_txs_to_hash = [r.to_dict() for r in rewards]
    merkle_root = ProofOfWork.calculate_merkle_root(all_txs_to_hash)
    bc.add_mining_job(merkle_root, [], rewards)
    
    ts = time.time()
    nonce, h = ProofOfWork.mine(index, last_block.hash, ts, merkle_root, winner, bc.target)
    
    submission = {
        "index": index, "previous_hash": last_block.hash, "timestamp": ts,
        "merkle_root": merkle_root, "validator": winner, "nonce": nonce, "hash": h
    }
    
    if bc.submit_block(submission):
        print("\n--- RESULTS ---")
        m1_bal = bc.get_balance("MINER_1") / 10**8
        m50_bal = bc.get_balance("MINER_50") / 10**8
        m100_bal = bc.get_balance("MINER_100") / 10**8
        m101_bal = bc.get_balance("MINER_101") / 10**8
        m200_bal = bc.get_balance("MINER_200") / 10**8
        
        print(f"MINER_1   (Winner + Top Active) : {m1_bal:.2f} $HOME")
        print(f"MINER_50  (Mid-Tier Active)     : {m50_bal:.2f} $HOME")
        print(f"MINER_100 (Last to get Reward)  : {m100_bal:.2f} $HOME")
        print(f"MINER_101 (Outside Top 100)     : {m101_bal:.2f} $HOME")
        print(f"MINER_200 (Least Active)        : {m200_bal:.2f} $HOME")
        
        print("\n[ANALYSIS]")
        print("1. Miner 101-200 mendapatkan 0 koin karena system membatasi distribusi ke TOP 100 teraktif.")
        print("2. Ini penting agar database blok tidak meledak ukurannya karena ribuan transaksi kecil (Dust).")
        print("3. Miner yang nambang di HP tetap dapet koin asalkan mereka masuk TOP 100 teraktif saat itu.")
    else:
        print("Block Rejected.")

if __name__ == "__main__":
    simulate_200_miners_fast()
