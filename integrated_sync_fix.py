import requests
import sqlite3
import re

# Extract config from supabase_sync.py
with open('supabase_sync.py', 'r') as f:
    content = f.read()
    sb_url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    sb_key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

print(f"[*] Using SB_URL: {sb_url}")

headers = {
    "apikey": sb_key,
    "Authorization": f"Bearer {sb_key}",
    "Content-Type": "application/json"
}

def sync_data():
    conn = sqlite3.connect('chain_v2.db')
    c = conn.cursor()
    
    # 1. Purge S_ labels
    print("[*] Purging S_ labels from Supabase...")
    url = f"{sb_url}/rest/v1/holders?address=like.S_*"
    res = requests.delete(url, headers=headers)
    print(f"    Status: {res.status_code}")
    
    # 2. Purge Truncated addresses
    print("[*] Purging truncated addresses...")
    truncated = ["aa0ba2e22c9cd4a6bc50b5c18bab9685ed69f9876e6b093390c7511d433644d96796646b212364c6e77b1ad57"]
    for addr in truncated:
        url = f"{sb_url}/rest/v1/holders?address=eq.{addr}"
        res = requests.delete(url, headers=headers)
        print(f"    Purge {addr[:8]}: {res.status_code}")

    # 3. Sync all local balances
    print("[*] Syncing local balances to Supabase...")
    c.execute("SELECT address, balance FROM balances WHERE balance > 0")
    holders = c.fetchall()
    
    payload = []
    for addr, bal in holders:
        payload.append({
            "address": addr,
            "balance": int(bal),
            "last_updated": "now()"
        })
    
    # Batch upsert
    batch_size = 100
    for i in range(0, len(payload), batch_size):
        batch = payload[i:i+batch_size]
        url = f"{sb_url}/rest/v1/holders"
        # We use POST with Prefer: resolution=merge-duplicates to upsert
        upsert_headers = headers.copy()
        upsert_headers["Prefer"] = "resolution=merge-duplicates"
        res = requests.post(url, headers=upsert_headers, json=batch)
        print(f"    Synced batch {i//batch_size + 1}: {res.status_code}")

    conn.close()
    print("[✓] Process Complete.")

if __name__ == "__main__":
    sync_data()
