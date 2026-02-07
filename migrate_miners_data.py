import sqlite3
import requests
import os

# --- MAPPING ---
M2_HEX = "01fbb49a2a9bbb6cb7b0034a7873497d39462615bc0fd9be4e8533c7a4966a3d"
M3_HEX = "04feaa27529d23357a829f07474476686a7d743a677b47423e20251759491696"

# Supabase Config
SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

def migrate_local():
    db_path = 'chain_v2.db'
    if not os.path.exists(db_path):
        print("chain_v2.db not found.")
        return
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Transfer balances
    for label, hex_addr in [("M2", M2_HEX), ("M3", M3_HEX)]:
        cur.execute("SELECT balance FROM balances WHERE address = ?", (label,))
        row = cur.fetchone()
        if row:
            balance = row[0]
            print(f"[*] Migrating {label} balance ({balance}) to {hex_addr[:16]}...")
            
            # Upsert hex balance
            cur.execute("INSERT INTO balances (address, balance) VALUES (?, ?) ON CONFLICT(address) DO UPDATE SET balance = balance + ?", (hex_addr, balance, balance))
            # Zero out or delete labels
            cur.execute("DELETE FROM balances WHERE address = ?", (label,))
            
            # Also update miner_activity if exists
            cur.execute("UPDATE miner_activity SET address = ? WHERE address = ?", (hex_addr, label))
            
    conn.commit()
    conn.close()
    print("[+] Local DB migration complete.")

def migrate_supabase():
    # 1. Get current M2/M3 balances from SB
    for label, hex_addr in [("M2", M2_HEX), ("M3", M3_HEX)]:
        try:
            url = f"{SB_URL}/rest/v1/holders?address=eq.{label}"
            res = requests.get(url, headers=headers)
            if res.status_code == 200 and res.json():
                balance = res.json()[0]['balance']
                print(f"[*] Migrating SB {label} balance ({balance}) to {hex_addr[:16]}...")
                
                # Update Hex Address balance
                # Note: PostgREST doesn't support complex increments easily via API, 
                # but we can try to upsert with the total.
                # First, get existing hex balance
                h_url = f"{SB_URL}/rest/v1/holders?address=eq.{hex_addr}"
                h_res = requests.get(h_url, headers=headers)
                existing_bal = 0
                if h_res.status_code == 200 and h_res.json():
                    existing_bal = h_res.json()[0]['balance']
                
                new_total = existing_bal + balance
                
                # Upsert Hex record
                upsert_data = {"address": hex_addr, "balance": new_total, "last_updated": "now()"}
                requests.post(f"{SB_URL}/rest/v1/holders", headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Prefer": "resolution=merge-duplicates"}, json=upsert_data)
                
                # Delete old string label
                requests.delete(url, headers=headers)
        except Exception as e:
            print(f"SB Migration Error for {label}: {e}")

if __name__ == "__main__":
    migrate_local()
    migrate_supabase()
    print("\n[SUCCESS] Addresses M2 and M3 have been mapped to their correct HEX addresses.")
