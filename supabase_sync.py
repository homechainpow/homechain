
import os
import time
import requests
import json
import datetime
import sys

# Configuration
NODE_URL = "http://localhost:5005"
SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def get_supabase_height():
    try:
        res = requests.get(f"{SB_URL}/rest/v1/blocks?select=id&order=id.desc&limit=1", headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data[0]['id'] + 1 if data else 0
    except Exception as e:
        print(f"[!] Error getting SB height: {e}", flush=True)
    return -1

def sync_entire_block(block):
    """Sync block, txs, and rewards in a single payload logic."""
    # 1. Block
    block_payload = {
        "id": block['index'],
        "hash": block['hash'],
        "prev_hash": block['previous_hash'],
        "timestamp": datetime.datetime.fromtimestamp(block['timestamp']).isoformat(),
        "validator": block['validator'],
        "tx_count": len(block['transactions']),
        "reward_count": len(block['rewards']),
        "target": str(block['target'])
    }
    
    # 2. Transactions
    tx_payloads = []
    for tx in block['transactions']:
        tx_payloads.append({
            "block_id": block['index'],
            "sender": tx['sender'],
            "receiver": tx['receiver'],
            "amount": tx['amount'],
            "data": tx.get('data'),
            "timestamp": datetime.datetime.fromtimestamp(tx.get('timestamp', block['timestamp'])).isoformat(),
            "signature": tx.get('signature')
        })
        
    # 3. Rewards
    reward_payloads = []
    for r in block['rewards']:
        reward_payloads.append({
            "block_id": block['index'],
            "receiver": r['receiver'],
            "amount": r['amount'],
            "timestamp": datetime.datetime.fromtimestamp(r.get('timestamp', block['timestamp'])).isoformat()
        })
        
    # Push to Supabase
    try:
        # Blocks
        requests.post(f"{SB_URL}/rest/v1/blocks", headers=headers, json=block_payload, timeout=5)
        # Txs
        if tx_payloads:
            requests.post(f"{SB_URL}/rest/v1/transactions", headers=headers, json=tx_payloads, timeout=5)
        # Rewards
        if reward_payloads:
            requests.post(f"{SB_URL}/rest/v1/rewards", headers=headers, json=reward_payloads, timeout=5)
    except Exception as e:
        print(f"[!] Sync Error on block {block['index']}: {e}", flush=True)

def update_stats(height, supply, difficulty):
    total_txs = 0
    try:
        # Count user transactions
        tx_count_res = requests.get(f"{SB_URL}/rest/v1/transactions?select=count", headers={**headers, "Range": "0-0"}, timeout=5)
        if tx_count_res.status_code == 200:
            data = tx_count_res.json()
            if data and len(data) > 0:
                total_txs += data[0].get('count', 0)
        
        # Count reward transactions
        reward_count_res = requests.get(f"{SB_URL}/rest/v1/rewards?select=count", headers={**headers, "Range": "0-0"}, timeout=5)
        if reward_count_res.status_code == 200:
            data = reward_count_res.json()
            if data and len(data) > 0:
                total_txs += data[0].get('count', 0)
    except Exception as e:
        print(f"[!] Error counting transactions: {e}", flush=True)
        total_txs = 0
    
    payload = {
        "id": 1,
        "height": height,
        "total_txs": total_txs,
        "last_updated": "now()"
    }
    if supply and int(supply) > 0:
        payload["total_supply"] = int(supply)
    if difficulty and difficulty != "---":
        payload["difficulty"] = str(difficulty)
        
    try:
        url = f"{SB_URL}/rest/v1/stats?id=eq.1"
        res = requests.patch(url, headers=headers, json=payload, timeout=5)
        if res.status_code not in [200, 201, 204]:
            requests.post(f"{SB_URL}/rest/v1/stats", headers=headers, json=payload, timeout=5)
    except Exception as e:
        print(f"[!] Update Stats Error: {e}", flush=True)

def sync_holders(node):
    """Sync all balances from SQLite to Supabase to overwrite buggy trigger math."""
    print("[*] Syncing holder balances from SQLite to Supabase...", flush=True)
    try:
        if not hasattr(node, 'conn'): node._init_db()
        node.cursor.execute("SELECT address, balance FROM balances")
        rows = node.cursor.fetchall()
        holders = [{"address": r[0], "balance": r[1], "last_updated": "now()"} for r in rows]
        
        for i in range(0, len(holders), 50):
            batch = holders[i:i+50]
            requests.post(f"{SB_URL}/rest/v1/holders", headers=headers, json=batch, timeout=10)
        print(f"[+] Synced {len(holders)} holders.", flush=True)
    except Exception as e:
        print(f"[!] Holder Sync Error: {e}", flush=True)

def main():
    print(f"=== HomeChain Supabase Sync Worker V4 (State Sync) Started at {datetime.datetime.now()} ===", flush=True)
    
    # Initialize Node to access SQLite
    sys.path.append(os.getcwd())
    from blockchain import Blockchain
    node = Blockchain()
    
    last_stat_update = 0
    
    while True:
        try:
            # 1. Determine Sync Start Point
            sb_height = get_supabase_height()
            if sb_height == -1:
                time.sleep(10)
                continue
                
            # 2. Get Blocks from Node
            batch_size = 50
            node_url = f"{NODE_URL}/blocks/range?start={sb_height}&end={sb_height + batch_size}"
            res = requests.get(node_url, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                blocks = data.get('blocks', [])
                for b in blocks:
                    print(f"[*] Syncing block #{b['index']}...", flush=True)
                    sync_entire_block(b)
            
            # Periodically sync all holder balances & stats (every 30 seconds)
            if time.time() - last_stat_update > 30:
                stats_res = requests.get(f"{NODE_URL}/chain", timeout=5)
                if stats_res.status_code == 200:
                    stats = stats_res.json()
                    update_stats(stats['length'], stats['supply'], "17")
                sync_holders(node)
                last_stat_update = time.time()
                
            time.sleep(5)
        except Exception as e:
            print(f"[!!] Main Loop Exception: {e}", flush=True)
            time.sleep(10)

if __name__ == "__main__":
    main()
