import sqlite3
import requests
import re
import json

# Config
DB_PATH = "C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/chain_v2.db"

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

def sync_all_holders():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT address, balance FROM balances WHERE balance > 0")
    holders = c.fetchall()
    conn.close()

    print(f"[*] Found {len(holders)} holders in local database.")
    
    payload = []
    for addr, bal in holders:
        payload.append({
            "address": addr,
            "balance": int(bal),
            "last_updated": "now()"
        })

    # Sync
    batch_size = 50
    for i in range(0, len(payload), batch_size):
        batch = payload[i:i+batch_size]
        res = requests.post(f"{sb_url}/rest/v1/holders", headers=headers, json=batch)
        print(f"    Synced batch {i//batch_size + 1}: {res.status_code}")

    print("[✓] All holders synchronized to Supabase.")

if __name__ == "__main__":
    sync_all_holders()
