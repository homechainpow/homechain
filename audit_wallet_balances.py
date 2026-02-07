import sqlite3
import json
import os

# Paths
MANIFEST_FILE = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/wallets_manifest.json'
DB_PATH = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/chain_v2.db'
BACKUP_DB = 'C:/Users/Administrator/.gemini/antigravity/scratch/backups/release_2.10_pre_push/HomeChain/chain_v2.db'
FINAL_AUDIT_FILE = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/wallets_final_audit.json'

def audit_balances():
    if not os.path.exists(MANIFEST_FILE):
        print(f"Error: {MANIFEST_FILE} not found.")
        return

    with open(MANIFEST_FILE, 'r') as f:
        manifest = json.load(f)

    # Connect to databases
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    conn_backup = sqlite3.connect(BACKUP_DB)
    c_backup = conn_backup.cursor()

    audit_results = []
    found_count = 0
    total_balance = 0

    print(f"[*] Auditing {len(manifest)} addresses...")

    for item in manifest:
        addr = item['address']
        pem_file = item['file']
        
        # Check current DB
        c.execute("SELECT balance FROM balances WHERE address = ?", (addr,))
        row = c.fetchone()
        
        balance = row[0] if row else 0
        
        # If 0, check backup DB (in case of recent reset/prune)
        if balance == 0:
            c_backup.execute("SELECT balance FROM balances WHERE address = ?", (addr,))
            row_backup = c_backup.fetchone()
            if row_backup:
                balance = row_backup[0]

        audit_results.append({
            "address": addr,
            "pem_file": pem_file,
            "balance": balance,
            "balance_home": balance / 10**8
        })
        
        if balance > 0:
            found_count += 1
            total_balance += balance

    print(f"[✓] Audit Complete.")
    print(f"    Wallets with balance > 0: {found_count}")
    print(f"    Total Balance Audited: {total_balance / 10**8:.2f} HOME")

    with open(FINAL_AUDIT_FILE, 'w') as f:
        json.dump(audit_results, f, indent=4)
    
    print(f"[*] Final Audit report saved to {FINAL_AUDIT_FILE}")

    conn.close()
    conn_backup.close()

if __name__ == "__main__":
    audit_balances()
