import sqlite3
import json
import os
import requests
import re

# Configuration
DB_PATH = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/chain_v2.db'
MAPPING_FILE = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/final_recovery_mapping.json'

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

def restore_properly():
    if not os.path.exists(MAPPING_FILE):
        print("Error: Mapping file not found.")
        return

    with open(MAPPING_FILE, 'r') as f:
        mapping = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print(f"[*] Restoring {len(mapping)} wallets...")
    
    payload = []
    restored_count = 0
    
    for label, info in mapping.items():
        hex_addr = info['hex']
        bal = info['balance']
        
        # 1. Update Local DB
        # Ensure address exists
        c.execute("INSERT OR IGNORE INTO balances (address, balance) VALUES (?, 0)", (hex_addr,))
        # Set balance (we use = bal instead of += because we are restoring from a snapshot)
        c.execute("UPDATE balances SET balance = ? WHERE address = ?", (bal, hex_addr))
        
        # 2. Add to Supabase payload
        payload.append({
            "address": hex_addr,
            "balance": bal,
            "last_updated": "now()"
        })
        restored_count += 1

    conn.commit()
    print(f"  [✓] Local DB updated ({restored_count} rows).")
    
    # 3. Sync to Supabase in batches
    print("[*] Syncing to Supabase...")
    batch_size = 50
    for i in range(0, len(payload), batch_size):
        batch = payload[i:i+batch_size]
        res = requests.post(f"{sb_url}/rest/v1/holders", headers=headers, json=batch)
        print(f"    Synced batch {i//batch_size + 1}: {res.status_code}")

    conn.close()
    print("[✓] Restoration Complete.")

if __name__ == "__main__":
    restore_properly()
