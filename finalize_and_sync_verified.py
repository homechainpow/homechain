import json
import requests
import re
import os

# Paths
FINAL_AUDIT_FILE = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/wallets_final_audit.json'
MANIFEST_BACKUP = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/verified_wallets_backup.json'
TEXT_LIST = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/verified_addresses_list.txt'

# Supabase Config
with open('C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/supabase_sync.py', 'r') as f:
    content = f.read()
    sb_url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    sb_key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

headers = {
    "apikey": sb_key,
    "Authorization": f"Bearer {sb_key}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def finalize_and_sync():
    if not os.path.exists(FINAL_AUDIT_FILE):
        print("Error: Audit file not found.")
        return

    with open(FINAL_AUDIT_FILE, 'r') as f:
        audit_data = json.load(f)

    # 1. Save Backup Files
    print("[*] Saving backup manifest and text list...")
    with open(MANIFEST_BACKUP, 'w') as f:
        json.dump(audit_data, f, indent=4)
    
    with open(TEXT_LIST, 'w') as f:
        for item in audit_data:
            f.write(f"{item['address']} ({item['pem_file']}) - Balance: {item['balance_home']} HOME\n")

    # 2. Prepare Supabase Payload
    payload = []
    for item in audit_data:
        payload.append({
            "address": item['address'],
            "balance": int(item['balance']),
            "last_updated": "now()"
        })

    # 3. Sync to Supabase
    print(f"[*] Syncing {len(payload)} verified wallets to Supabase...")
    batch_size = 50
    for i in range(0, len(payload), batch_size):
        batch = payload[i:i+batch_size]
        res = requests.post(f"{sb_url}/rest/v1/holders", headers=headers, json=batch)
        print(f"    Synced batch {i//batch_size + 1}: {res.status_code}")

    print("[✓] Process Complete.")

if __name__ == "__main__":
    finalize_and_sync()
