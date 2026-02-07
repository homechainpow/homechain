import subprocess
import json
import requests
import sqlite3
import os

# Supabase credentials
SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlmXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def sync_from_remote_s1():
    print("=== Syncing from S1 (Authoritative Chain) ===")
    
    # Use a more reliable way to run multi-line python on remote
    remote_script = """
import sqlite3, json, os
db_path = 'HomeChain/chain_v2.db'
if not os.path.exists(db_path):
    print('ERROR: DB NOT FOUND')
    exit(1)
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('SELECT address, balance FROM balances WHERE balance > 0')
rows = c.fetchall()
print(json.dumps([{'address': r[0], 'balance': r[1]} for r in rows]))
"""
    
    ssh_cmd = [
        "ssh", "-i", "C:/D/xelis1.pem", "-o", "StrictHostKeyChecking=no",
        "ubuntu@ec2-3-84-153-5.compute-1.amazonaws.com",
        f"python3 -c {json.dumps(remote_script)}"
    ]
    
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True)
        # Filter out potential warnings from SSH
        json_start = result.stdout.find('[{"address":')
        if json_start == -1:
            print(f"[!] Output does not contain expected JSON: {result.stdout}")
            return
        
        s1_holders = json.loads(result.stdout[json_start:])
        print(f"[*] Fetched {len(s1_holders)} holders from S1.")
    except Exception as e:
        print(f"[!] Failed to fetch from S1: {e}")
        if hasattr(e, 'stderr'): print(f"DEBUG Error: {e.stderr}")
        return

    # 2. Upsert to Supabase
    batch_size = 50
    synced = 0
    for i in range(0, len(s1_holders), batch_size):
        batch = s1_holders[i:i+batch_size]
        res = requests.post(f"{SB_URL}/rest/v1/holders", headers=headers, json=batch)
        if res.status_code in [200, 201, 204]:
            synced += len(batch)
            print(f"  [+] Synced {synced}/{len(s1_holders)} holders...", end="\r")
        else:
            print(f"  [!] Failed batch {i//batch_size + 1}: {res.text}")
    print(f"\n[✓] Supabase Holders Synced ({synced} total).")

    # 3. Update Stats Table
    total_supply = sum(h['balance'] for h in s1_holders)
    # Get max height from S1 too
    ssh_cmd_height = ["ssh", "-i", "C:/D/xelis1.pem", "-o", "StrictHostKeyChecking=no", "ubuntu@ec2-3-84-153-5.compute-1.amazonaws.com", "python3 -c \"import sqlite3; conn = sqlite3.connect('HomeChain/chain_v2.db'); c = conn.cursor(); c.execute('SELECT MAX(idx) FROM blocks'); print(c.fetchone()[0])\""]
    height_res = subprocess.run(ssh_cmd_height, capture_output=True, text=True).stdout.strip()
    height = int(height_res) if height_res.isdigit() else 367

    stats_payload = {
        "supply": total_supply,
        "height": height,
        "difficulty": 1 # Placeholder or fetch from S1
    }
    requests.patch(f"{SB_URL}/rest/v1/stats?id=eq.1", headers=headers, json=stats_payload)
    print(f"[✓] Stats updated: Height={height}, Supply={total_supply/100000000:.2f} HOME")

if __name__ == "__main__":
    sync_from_remote_s1()
