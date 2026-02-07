import requests
import json
import sqlite3

# --- SETTINGS ---
SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlmXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def sync_all_to_sb():
    print("🔄 Starting Full Supabase Sync (Accurate Balances)...")
    
    conn = sqlite3.connect('chain_v2.db')
    c = conn.cursor()
    c.execute("SELECT address, balance FROM balances WHERE balance > 0")
    local_data = c.fetchall()
    conn.close()
    
    print(f"[*] Found {len(local_data)} holders to sync.")
    
    holders_payload = []
    for addr, bal in local_data:
        holders_payload.append({
            "address": addr,
            "balance": int(bal),
            "last_updated": "now()"
        })

    # Sync in batches of 50
    batch_size = 50
    for i in range(0, len(holders_payload), batch_size):
        batch = holders_payload[i:i+batch_size]
        res = requests.post(f"{SB_URL}/rest/v1/holders", headers=headers, json=batch)
        if res.status_code in [200, 201, 204]:
            print(f"  [+] Batched {i+len(batch)} holders synced.")
        else:
            print(f"  [!] Batch Error: {res.status_code} - {res.text}")

    print("✨ Sync Complete.")

if __name__ == "__main__":
    sync_all_to_sb()
