import sqlite3
import requests
import json
import re
import time

# Configuration
with open('supabase_sync.py', 'r') as f:
    content = f.read()
    sb_url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    sb_key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

headers = {
    "apikey": sb_key,
    "Authorization": f"Bearer {sb_key}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def sync_all():
    conn = sqlite3.connect('chain_v2.db')
    c = conn.cursor()
    
    # 1. Sync Holders
    print("[*] Syncing Holders...")
    c.execute("SELECT address, balance FROM balances WHERE balance > 0")
    holders = [{"address": r[0], "balance": int(r[1]), "last_updated": "now()"} for r in c.fetchall()]
    print(f"    Total Holders to sync: {len(holders)}")
    for i in range(0, len(holders), 100):
        requests.post(f"{sb_url}/rest/v1/holders", headers=headers, json=holders[i:i+100])
    
    # 2. Sync Blocks (Last 500)
    # Local table 'blocks' uses 'idx' instead of 'id'
    print("[*] Syncing Blocks...")
    c.execute("SELECT idx, hash, prev_hash, timestamp, data FROM blocks ORDER BY idx DESC LIMIT 500")
    block_records = c.fetchall()
    
    blocks_payload = []
    for r in block_records:
        data = json.loads(r[4])
        blocks_payload.append({
            "id": r[0],
            "hash": r[1],
            "prev_hash": r[2],
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(r[3])),
            "validator": data.get('validator', 'UNKNOWN'),
            "tx_count": len(data.get('transactions', [])),
            "reward_count": len(data.get('rewards', [])),
            "difficulty": str(data.get('target', ''))
        })

    if blocks_payload:
        for i in range(0, len(blocks_payload), 50):
            res = requests.post(f"{sb_url}/rest/v1/blocks", headers=headers, json=blocks_payload[i:i+50])
            print(f"    Synced blocks batch {i//50 + 1}: {res.status_code}")

    # 3. Sync Transactions & Rewards from these blocks
    for b in blocks_payload:
        b_idx = b['id']
        c.execute("SELECT data FROM blocks WHERE idx = ?", (b_idx,))
        b_data = json.loads(c.fetchone()[0])
        
        # Transactions
        txs = b_data.get('transactions', [])
        if txs:
            tx_list = [{
                "block_id": b_idx,
                "sender": t.get('sender', 'UNKNOWN'),
                "receiver": t.get('receiver', 'UNKNOWN'),
                "amount": int(t.get('amount', 0)),
                "fee": int(t.get('fee', 1000000)),
                "timestamp": b['timestamp'],
                "signature": t.get('signature', '')
            } for t in txs]
            requests.post(f"{sb_url}/rest/v1/transactions", headers=headers, json=tx_list)
            
        # Rewards
        rews = b_data.get('rewards', [])
        if rews:
            rew_list = [{
                "block_id": b_idx,
                "receiver": r.get('receiver', 'UNKNOWN'),
                "amount": int(r.get('amount', 0)),
                "type": r.get('data', {}).get('type', 'reward'),
                "timestamp": b['timestamp']
            } for r in rews]
            requests.post(f"{sb_url}/rest/v1/rewards", headers=headers, json=rew_list)

    print("[✓] Full Production Sync Complete.")
    conn.close()

if __name__ == "__main__":
    sync_all()
