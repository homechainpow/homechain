import requests
import time
import json
import os
import sys
import datetime

# --- CONFIGURATION ---
NODE_URL = "http://localhost:5005" 
SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def get_supabase_height():
    """Returns the next block index to sync or -1 on error."""
    try:
        url = f"{SB_URL}/rest/v1/blocks?select=id&order=id.desc&limit=1"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            print(f"[*] SB Height Raw Data: {data}", flush=True)
            if data:
                h = int(data[0]['id']) + 1
                print(f"[*] SB Height Check: {h}", flush=True)
                return h
            print("[*] SB Height Check: 0 (Empty)", flush=True)
            return 0 # Fresh DB
        print(f"[!] SB Height Error: {res.status_code} - {res.text}", flush=True)
    except Exception as e:
        print(f"[!] SB Height Exception: {e}", flush=True)
    return -1

def post_to_sb(table, data):
    """Posts data to Supabase. Returns True if success or duplicate."""
    url = f"{SB_URL}/rest/v1/{table}"
    try:
        res = requests.post(url, headers=headers, json=data, timeout=15)
        if res.status_code in [200, 201, 204]:
            return True
        print(f"[!] SB Post Error ({table}): {res.status_code} - {res.text}", flush=True)
        return False
    except Exception as e:
        print(f"[!] SB Post Exception ({table}): {e}", flush=True)
        return False

def sync_block(b):
    """Syncs a single block and its components."""
    # print(f"[*] Syncing Block #{b['index']}...", flush=True)
    
    # 1. Blocks Table
    block_data = {
        "id": b['index'],
        "hash": b['hash'],
        "prev_hash": b.get('previous_hash', ''),
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(b['timestamp'])),
        "validator": b['validator'],
        "tx_count": len(b.get('transactions', [])),
        "reward_count": len(b.get('rewards', [])),
        "target": str(b['target']),
        "difficulty": str(b.get('target', ''))
    }
    if not post_to_sb("blocks", block_data):
        return False
        
    # 2. Transactions Table
    txs = b.get('transactions', [])
    if txs:
        tx_list = [{
            "block_id": b['index'],
            "sender": t.get('sender', 'UNKNOWN'),
            "receiver": t.get('receiver', 'UNKNOWN'),
            "amount": int(t.get('amount', 0)),
            "data": json.dumps(t.get('data')) if isinstance(t.get('data'), (dict, list)) else str(t.get('data')),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t.get('timestamp', b['timestamp']))),
            "signature": t.get('signature', '')
        } for t in txs]
        if post_to_sb("transactions", tx_list):
            print(f"[+] Posted {len(tx_list)} transactions for Block #{b['index']}", flush=True)
        
    # 3. Rewards Table
    rewards = b.get('rewards', [])
    if rewards:
        rew_list = [{
            "block_id": b['index'],
            "receiver": r.get('receiver', 'UNKNOWN'),
            "amount": int(r.get('amount', 0)),
            "type": r.get('data', {}).get('type', 'reward'),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(r.get('timestamp', b['timestamp'])))
        } for r in rewards]
        post_to_sb("rewards", rew_list)
        
    return True

def update_stats(height, supply, difficulty):
    """Updates network statistics."""
    payload = {
        "id": 1,
        "height": height,
        "last_updated": "now()"
    }
    # Only update supply if we actually got a value
    if supply and int(supply) > 0:
        payload["total_supply"] = int(supply)
    
    # Only update difficulty if we have a real value
    if difficulty and difficulty != "---":
        payload["difficulty"] = str(difficulty)
        
    url = f"{SB_URL}/rest/v1/stats?id=eq.1"
    try:
        res = requests.patch(url, headers=headers, json=payload, timeout=5)
        if res.status_code not in [200, 201, 204]:
            # Maybe id=1 doesn't exist yet
            requests.post(f"{SB_URL}/rest/v1/stats", headers=headers, json=payload, timeout=5)
    except Exception as e:
        print(f"[!] Update Stats Error: {e}", flush=True)

def main():
    print(f"=== HomeChain Supabase Sync Worker V3 Started at {datetime.datetime.now()} ===", flush=True)
    
    while True:
        try:
            # 1. Determine Sync Start Point
            sb_height = get_supabase_height()
            if sb_height == -1:
                print("[-] Supabase unreachable. Retrying in 10s...", flush=True)
                time.sleep(10)
                continue
                
            # 2. Check Node Height & Get Blocks
            # Fetch batch of 100 for speed
            batch_size = 100
            node_url = f"{NODE_URL}/blocks/range?start={sb_height}&end={sb_height + batch_size}"
            res = requests.get(node_url, timeout=10)
            
            if res.status_code != 200:
                # print(f"[-] Node API Error: {res.status_code}. Waiting...", flush=True)
                time.sleep(5)
                continue
                
            data = res.json()
            blocks = data.get('blocks', [])
            total_chain = data.get('total', 0)
            
            # Fetch supply occasionally if available, or use node_data
            supply = 0
            try:
                supply_res = requests.get(f"{NODE_URL}/chain", timeout=5)
                if supply_res.status_code == 200:
                    supply = supply_res.json().get('supply', 0)
            except: pass

            # Update stats even if caught up (to refresh supply/last_updated)
            if total_chain >= 0:
                # We use sb_height or total_chain? sb_height is safer for 'current height'
                # For difficulty, we'd need to fetch a block, but let's just keep height/supply updated
                update_stats(sb_height, supply, "---") # difficulty will be fetched from block if syncing

            if not blocks:
                # print(f"[.] Caught up at height {sb_height}.", end="\r", flush=True)
                time.sleep(5)
                continue
                
            print(f"[*] Syncing: SB={sb_height} | Node={total_chain} | Batch={len(blocks)}", flush=True)
            
            synced_in_batch = 0
            for b in blocks:
                if sync_block(b):
                    sb_height = b['index'] + 1
                    synced_in_batch += 1
                    # Update stats per block for real-time feel
                    diff_val = b.get('target', '---')
                    update_stats(b['index'], supply, diff_val)
                    print(f"[*] Block #{b['index']} synced. (Current SB Height: {sb_height})", flush=True)
                else:
                    print(f"[!] Block {b['index']} sync FAILED. Breaking batch.", flush=True)
                    break
            
            if synced_in_batch > 0:
                last_b = blocks[synced_in_batch-1]
                print(f"[+] Synced up to block #{last_b['index']} (Supply: {supply})", flush=True)
                
        except Exception as e:
            print(f"[-] Main Loop Exception: {e}", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
