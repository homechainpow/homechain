import requests
import sqlite3
import re
import json
import time

# Config
DB_PATH = "C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/chain_v2.db"

with open('supabase_sync.py', 'r') as f:
    content = f.read()
    sb_url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    sb_key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

headers = {
    "apikey": sb_key,
    "Authorization": f"Bearer {sb_key}",
    "Content-Type": "application/json"
}

def reset_and_sync():
    print("=== Master Sync Reset & Restoration Started ===")
    
    # 1. Purge Supabase (Delete from all tables)
    tables = ["transactions", "rewards", "blocks", "holders"]
    for table in tables:
        print(f"[*] Purging table: {table}...")
        res = requests.delete(f"{sb_url}/rest/v1/{table}?id=gt.0", headers=headers)
        if table == "holders":
            # For holders we might need a different filter if id doesn't exist or is different
            requests.delete(f"{sb_url}/rest/v1/{table}?balance=gte.0", headers=headers)
        print(f"    Purge result: {res.status_code}")

    # 2. Re-Sync Holders
    print("\n[*] Syncing Holders from Local DB...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT address, balance FROM balances WHERE balance > 0")
    holders = [{"address": r[0], "balance": int(r[1]), "last_updated": "now()"} for r in c.fetchall()]
    
    batch_size = 100
    for i in range(0, len(holders), batch_size):
        requests.post(f"{sb_url}/rest/v1/holders", headers=headers, json=holders[i:i+batch_size])
    print(f"    Total Holders Synced: {len(holders)}")

    # 3. Re-Sync Blocks
    print("\n[*] Syncing Blocks, Transactions, and Rewards...")
    c.execute("SELECT idx, hash, prev_hash, timestamp, data FROM blocks ORDER BY idx ASC")
    all_blocks = c.fetchall()
    
    for r in all_blocks:
        b_idx = r[0]
        data = json.loads(r[4])
        
        # Block entry
        block_payload = {
            "id": b_idx,
            "hash": r[1],
            "prev_hash": r[2],
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(r[3])),
            "validator": data.get('validator', 'UNKNOWN'),
            "tx_count": len(data.get('transactions', [])),
            "reward_count": len(data.get('rewards', [])),
            "difficulty": str(data.get('target', ''))
        }
        requests.post(f"{sb_url}/rest/v1/blocks", headers=headers, json=block_payload)
        
        # Transactions
        txs = data.get('transactions', [])
        if txs:
            tx_list = [{
                "block_id": b_idx,
                "sender": t.get('sender', 'UNKNOWN'),
                "receiver": t.get('receiver', 'UNKNOWN'),
                "amount": int(t.get('amount', 0)),
                "fee": int(t.get('fee', 1000000)),
                "timestamp": block_payload['timestamp'],
                "signature": t.get('signature', '')
            } for t in txs]
            requests.post(f"{sb_url}/rest/v1/transactions", headers=headers, json=tx_list)
            
        # Rewards
        rews = data.get('rewards', [])
        if rews:
            rew_list = [{
                "block_id": b_idx,
                "receiver": r.get('receiver', 'UNKNOWN'),
                "amount": int(r.get('amount', 0)),
                "type": r.get('data', {}).get('type', 'reward'),
                "timestamp": block_payload['timestamp']
            } for r in rews]
            requests.post(f"{sb_url}/rest/v1/rewards", headers=headers, json=rew_list)
            
        if b_idx % 50 == 0:
            print(f"    Processed up to Block #{b_idx}")

    print("\n[✓] Master Sync Reset & Restoration Complete.")
    conn.close()

if __name__ == "__main__":
    reset_and_sync()
