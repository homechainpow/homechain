import sqlite3
import requests
import json
import os
from wallet import Wallet

# Supabase credentials
SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def sync_all_holders():
    print("=== Starting 100% Accuracy Sync ===")
    
    # 1. Fetch all balances from local DB
    conn = sqlite3.connect('chain_v2.db')
    c = conn.cursor()
    c.execute("SELECT address, balance FROM balances WHERE balance > 0")
    local_data = c.fetchall()
    conn.close()
    
    print(f"[*] Found {len(local_data)} active holders in local DB.")
    
    # 2. Use Upsert (POST with Prefer: resolution=merge-duplicates)
    headers_upsert = headers.copy()
    headers_upsert["Prefer"] = "resolution=merge-duplicates"
    
    holders_to_sync = [{"address": r[0], "balance": r[1]} for r in local_data]
    
    batch_size = 50
    synced = 0
    for i in range(0, len(holders_to_sync), batch_size):
        batch = holders_to_sync[i:i+batch_size]
        res = requests.post(f"{SB_URL}/rest/v1/holders", headers=headers_upsert, json=batch)
        if res.status_code in [200, 201, 204]:
            synced += len(batch)
            print(f"  [+] Synced {synced}/{len(holders_to_sync)} holders...")
        else:
            print(f"  [!] Failed batch {i//batch_size + 1}: {res.text}")

    print("[✓] Holders Sync Complete.")

def backup_miners():
    print("\n=== Backing up Miner Wallets ===")
    miner_keys = {
        'S1': 'C:/D/xelis1.pem',
        'S2': 'C:/D/arduino1.pem',
        'S3': 'C:/D/miner.pem'
    }
    
    backup_data = []
    
    # Ensure current dir is in path for imports if needed
    import sys
    sys.path.append(os.getcwd())
    
    for name, path in miner_keys.items():
        if os.path.exists(path):
            try:
                # Use absolute path and verify file readability
                with open(path, 'r') as f:
                    content = f.read()
                
                # Try to load via Wallet class
                w = Wallet.load_from_pem(path)
                backup_data.append({
                    "name": name,
                    "pem_path": path,
                    "address": w.address
                })
                print(f"  [+] Found {name}: {w.address[:16]}...")
            except Exception as e:
                print(f"  [!] Failed to load {name} at {path}: {e}")
        else:
            print(f"  [!] {name} key not found at {path}")

    # Also check local wallets folder
    wallet_dir = 'wallets'
    for f in os.listdir(wallet_dir):
        if 'miner' in f.lower() or 'vps' in f.lower():
            try:
                w = Wallet.load_from_pem(os.path.join(wallet_dir, f))
                backup_data.append({
                    "name": f,
                    "pem_path": os.path.join(wallet_dir, f),
                    "address": w.address
                })
                print(f"  [+] Found {f}: {w.address[:16]}...")
            except:
                pass

    with open('miner_backup.json', 'w') as f:
        json.dump(backup_data, f, indent=4)
    print(f"[✓] Backup saved to miner_backup.json")

if __name__ == "__main__":
    sync_all_holders()
    backup_miners()
