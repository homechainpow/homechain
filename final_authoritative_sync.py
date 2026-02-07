import requests
import sqlite3
import re
import json
import time
import os

# --- SETTINGS ---
DB_PATH = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/chain_v2.db'
REPLAYED_STATE_PATH = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/REPLAYED_STATE.json'
MANIFEST_PATH = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/MASTER_WALLETS_MANIFEST.json'

with open('C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/supabase_sync.py', 'r') as f:
    content = f.read()
    sb_url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    sb_key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

headers = {
    "apikey": sb_key,
    "Authorization": f"Bearer {sb_key}",
    "Content-Type": "application/json"
}

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def final_authoritative_sync():
    print("=== Final Authoritative Sync Restoration ===")
    
    # 1. Purge Supabase (All Tables)
    tables = ["transactions", "rewards", "blocks", "holders"]
    for table in tables:
        print(f"[*] Purging production table: {table}...")
        requests.delete(f"{sb_url}/rest/v1/{table}?id=gt.0", headers=headers)
        if table == "holders":
            requests.delete(f"{sb_url}/rest/v1/{table}?balance=gte.0", headers=headers)

    # 2. Sync Replayed Holders
    print("\n[*] Syncing Replayed Holders...")
    replayed_balances = load_json(REPLAYED_STATE_PATH)
    holders_payload = []
    for addr, bal in replayed_balances.items():
        holders_payload.append({
            "address": addr,
            "balance": int(bal),
            "last_updated": "now()"
        })
    
    batch_size = 100
    for i in range(0, len(holders_payload), batch_size):
        requests.post(f"{sb_url}/rest/v1/holders", headers=headers, json=holders_payload[i:i+batch_size])
    print(f"    Synced {len(holders_payload)} holders.")

    # 3. Sync Blocks & History (Blockchain-True)
    print("\n[*] Syncing Blocks, Transactions, and Rewards (Authoritative)...")
    
    # Load manifest for label resolution
    manifest = load_json(MANIFEST_PATH)
    label_to_hex = {}
    for hex_addr, files in manifest.items():
        for f_info in files:
            match = re.search(r'(p\d+)\.pem', f_info)
            if match:
                p_num = int(match.group(1)[1:])
                if 1 <= p_num <= 100: label_to_hex[f"S_{900 + p_num}"] = hex_addr
                elif 201 <= p_num <= 281: label_to_hex[f"S_{900 + p_num}"] = hex_addr

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT idx, hash, prev_hash, timestamp, data FROM blocks ORDER BY idx ASC")
    
    for r in c.fetchall():
        b_idx = r[0]
        data = json.loads(r[4])
        ts_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(r[3]))
        
        # Block
        requests.post(f"{sb_url}/rest/v1/blocks", headers=headers, json={
            "id": b_idx, "hash": r[1], "prev_hash": r[2], "timestamp": ts_str,
            "validator": data.get('validator', 'UNKNOWN'),
            "tx_count": len(data.get('transactions', [])),
            "reward_count": len(data.get('rewards', [])),
            "difficulty": str(data.get('target', ''))
        })
        
        # Transactions (mapped)
        txs = data.get('transactions', [])
        if txs:
            tx_payload = [{
                "block_id": b_idx,
                "sender": label_to_hex.get(t.get('sender'), t.get('sender')),
                "receiver": label_to_hex.get(t.get('receiver'), t.get('receiver')),
                "amount": int(t.get('amount', 0)),
                "fee": int(t.get('fee', 1000000)),
                "timestamp": ts_str,
                "signature": t.get('signature', '')
            } for t in txs]
            requests.post(f"{sb_url}/rest/v1/transactions", headers=headers, json=tx_payload)
            
        # Rewards (mapped)
        rews = data.get('rewards', [])
        if rews:
            rew_payload = [{
                "block_id": b_idx,
                "receiver": label_to_hex.get(rew.get('receiver'), rew.get('receiver')),
                "amount": int(rew.get('amount', 0)),
                "type": rew.get('data', {}).get('type', 'reward'),
                "timestamp": ts_str
            } for rew in rews]
            requests.post(f"{sb_url}/rest/v1/rewards", headers=headers, json=rew_payload)
            
        if b_idx % 50 == 0:
            print(f"    Processed Block #{b_idx}")

    print("\n[✓] Final Authoritative Sync Complete.")
    conn.close()

if __name__ == "__main__":
    final_authoritative_sync()
