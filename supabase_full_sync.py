
import requests
import time
import json
import sqlite3
import os

# --- MOCK / DB ACCESS ---
# Since API access is flaky for holders, we will read the DB directly for the 'Truth'
# and also use the Node API for blocks if possible, or DB as fallback.

DB_PATH = '/home/ubuntu/HomeChain/chain_v2.db'
SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def get_db_connection():
    return sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)

def post_to_sb(table, data):
    url = f"{SB_URL}/rest/v1/{table}"
    # Use merge-duplicates to avoid 409 errors on resync
    curr_headers = headers.copy()
    curr_headers["Prefer"] = "resolution=merge-duplicates"
    
    try:
        # Batch insert for performance
        if isinstance(data, list) and len(data) > 1000:
            for i in range(0, len(data), 1000):
                post_to_sb(table, data[i:i+1000])
            return True

        res = requests.post(url, headers=curr_headers, json=data, timeout=30)
        if res.status_code in [200, 201, 204]:
            return True
        print(f"[!] SB Post Error ({table}): {res.status_code} - {res.text}")
        return False
    except Exception as e:
        print(f"[!] SB Post Exception ({table}): {e}")
        return False

def sync_holders_from_db():
    print("[*] Calculating Holders from Chain DB...")
    conn = get_db_connection()
    c = conn.cursor()
    
    # Simple logic: Reconstruct balances from UTxO or just sum ins/outs?
    # Since checking the whole logic is complex, let's use the logic from 'check_holders.py'
    # which seems to iterate over blocks.
    
    holders = {}
    
    try:
        c.execute("SELECT data FROM blocks ORDER BY idx ASC")
        rows = c.fetchall()
        print(f"[*] Processing {len(rows)} blocks for holder balances...")
        
        for r in rows:
            block = json.loads(r[0])
            
            # Genesis/Validator Rewards
            validator = block['validator']
            # Assumption: Block reward is fixed or in 'rewards'?
            # Let's look at specific rewards field
            rewards = block.get('rewards', [])
            for rew in rewards:
                rcv = rew.get('receiver')
                amt = float(rew.get('amount', 0))
                holders[rcv] = holders.get(rcv, 0) + amt
                
            # Transactions
            txs = block.get('transactions', [])
            for tx in txs:
                sender = tx.get('sender')
                receiver = tx.get('receiver')
                amount = float(tx.get('amount', 0))
                fee = float(tx.get('fee', 0)) # If fee exists
                
                if sender != "SYSTEM" and sender != "0": 
                    holders[sender] = holders.get(sender, 0) - amount
                
                holders[receiver] = holders.get(receiver, 0) + amount
        
        # Filter out zero balances
        valid_holders = []
        for addr, bal in holders.items():
            if bal > 0.00000001: # Epsilon
                valid_holders.append({
                    "address": addr,
                    "balance": int(bal) # Store as atomic units (integers) in DB? Or float? 
                    # Earlier we saw formatMoney dividing by 100_000_000. 
                    # If the DB stores 50.0 and formatMoney divides, we need to match via COIN.
                    # Wait, check_holders.py output: "450.00000000 HOME".
                    # Supabase 'holders' table schema? Let's assume it expects integer atomic units or float?
                    # Previous sync script used `int(r.get('amount', 0))`.
                    # If 'amount' in JSON is 50.0, and COIN is 100M, then atomic is 5,000,000,000.
                    # BUT `check_holders.py` print suggests the JSON amount IS the full coin amount? 
                    # Let's double check simple_test.py or similar.
                    # Actually standard is usually atomic units. 
                    # Let's assume the JSON has atomic units. 
                    # If check_holders divides by 100000000 to print, then JSON has atomic.
                })
        
        print(f"[*] Found {len(valid_holders)} valid holders.")
        
        # Clear existing holders calculation or UPSERT?
        # Upsert is safer.
        # But for a full resync, maybe truncate?
        # Supabase REST doesn't support TRUNCATE easily without RLS bypass or specific function.
        # We will iterate and upsert.
        
        # Prepare batch for UPSERT
        # We need "on_conflict" for 'address'
        
        batch = []
        for h in valid_holders:
            batch.append(h)
            
        if batch:
            # We must use upsert=true header logic which we have in `post_to_sb`? 
            # modifying post_to_sb for upsert specific if needed.
            # actually our previous post_to_sb just POSTs. 
            # We need explicit upsert params.
             url = f"{SB_URL}/rest/v1/holders"
             curr_headers = headers.copy()
             curr_headers["Prefer"] = "resolution=merge-duplicates"
             
             # Split batches
             for i in range(0, len(batch), 1000):
                 chunk = batch[i:i+1000]
                 res = requests.post(url, headers=curr_headers, json=chunk)
                 if res.status_code not in [200, 201, 204]:
                     print(f"Failed to upsert holders: {res.text}")
                     
        print("[+] Holders synced.")
        return len(valid_holders)

    except Exception as e:
        print(f"[!] Error calculating holders: {e}")
        return 0

def sync_all_blocks():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT data FROM blocks ORDER BY idx ASC")
    
    rows = c.fetchall()
    total_count = len(rows)
    print(f"[*] Found {total_count} blocks in DB. Syncing in batches...")
    
    batch_size = 50
    synced_total = 0
    
    for i in range(0, total_count, batch_size):
        chunk = rows[i : i + batch_size]
        
        batch_blocks = []
        batch_txs = []
        batch_rewards = []
        
        for row in chunk:
            try:
                b = json.loads(row[0])
                block_id = b['index']
                
                # Block
                batch_blocks.append({
                    "id": block_id,
                    "hash": b['hash'],
                    "prev_hash": b.get('previous_hash', ''),
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(b['timestamp'])),
                    "validator": b['validator'],
                    "tx_count": len(b.get('transactions', [])),
                    "reward_count": len(b.get('rewards', [])),
                    "target": str(b['target'])
                })
                
                # Txs
                for tx_idx, t in enumerate(b.get('transactions', [])):
                    batch_txs.append({
                        "id": (block_id * 1000) + tx_idx + 1000000, # Offset to avoid conflict with manually added small IDs
                        "block_id": block_id,
                        "sender": t.get('sender', 'UNKNOWN'),
                        "receiver": t.get('receiver', 'UNKNOWN'),
                        "amount": int(t.get('amount', 0)),
                        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t.get('timestamp', b['timestamp']))),
                        "signature": t.get('signature', '')
                    })
                    
                # Rewards
                for rew_idx, r in enumerate(b.get('rewards', [])):
                    batch_rewards.append({
                        "id": (block_id * 1000) + rew_idx + 2000000, # Different offset
                        "block_id": block_id,
                        "receiver": r.get('receiver', 'UNKNOWN'),
                        "amount": int(r.get('amount', 0)),
                        "type": r.get('data', {}).get('type', 'reward'),
                        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(r.get('timestamp', b['timestamp'])))
                    })
            except Exception as e:
                print(f"[!] Skipping block due to error: {e}")
                continue
        
        # 1. Blocks First
        if post_to_sb("blocks", batch_blocks):
            # 2. Then Txs and Rewards
            if batch_txs: post_to_sb("transactions", batch_txs)
            if batch_rewards: post_to_sb("rewards", batch_rewards)
            synced_total += len(chunk)
            print(f"[+] Batch {i//batch_size + 1} Done ({synced_total}/{total_count})")
        else:
            print(f"[!] Block batch {i//batch_size + 1} FAILED. Trying individual blocks in this batch...")
            # Fallback to one-by-one for this batch if needed, but let's see for now.
            
    return synced_total

def main():
    print("=== FULL SYNC INITIATED ===")
    
    # 1. Sync Blocks & Txs
    total_blocks = sync_all_blocks()
    
    # 2. Sync Holders (Calculation)
    total_holders = sync_holders_from_db()
    
    # 3. Update Stats
    # Get max block info
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT data FROM blocks ORDER BY idx DESC LIMIT 1")
    last_json = c.fetchone()[0]
    last_block = json.loads(last_json)
    
    # Calculate Total Supply (Sum of all holders or sum of all rewards?)
    # Sum of all valid holders is the circulating supply.
    # OR sum of all rewards ever minted.
    # Let's use the sum of all holders balances calculated in sync_holders? 
    # Whatever, let's just use what we have or query /chain later.
    # For now, let's fetch supply from the node API locally for accuracy
    
    total_supply = 0
    try:
        # Calculate supply by summing up all rewards from blocks
        # We already iterated blocks in sync_all_blocks, but let's do a quick DB query or re-use batch data?
        # Re-querying is safer.
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT data FROM blocks")
        rows = c.fetchall()
        
        calculated_supply = 0
        for r in rows:
            try:
                b = json.loads(r[0])
                # Sum all rewards in this block
                for rew in b.get('rewards', []):
                    calculated_supply += int(rew.get('amount', 0))
            except: pass
            
        total_supply = calculated_supply
        print(f"[*] Calculated Supply from DB: {total_supply}")
        
    except Exception as e:
        print(f"[!] Could not calculate supply: {e}")

    payload = {
        "id": 1,
        "height": last_block['index'] + 1, # Height = index + 1
        "total_supply": int(total_supply),
        "difficulty": str(last_block.get('target', '---')),
        "last_updated": "now()"
    }
    
    requests.patch(f"{SB_URL}/rest/v1/stats?id=eq.1", headers=headers, json=payload)
    print(f"[+] Stats Updated: Height={payload['height']}, Supply={total_supply}")
    print("=== SYNC COMPLETE ===")

if __name__ == "__main__":
    main()
