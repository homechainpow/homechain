
import sqlite3
import json
import os
import glob

DB_PATH = '/home/ubuntu/HomeChain/chain_v2.db'
WALLETS_ROOT = '/home/ubuntu/HomeChain'

def get_db_connection():
    return sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)

def audit_wallets_on_disk():
    print("--- 1. AUDIT: WALLET FILES ON DISK ---")
    wallet_files = []
    # Search recursively for wallet_*.json or just *.json in suspected folders
    search_paths = [
        f"{WALLETS_ROOT}/wallets",
        f"{WALLETS_ROOT}/wallets_300",
        f"{WALLETS_ROOT}/wallets_parallel"
    ]
    
    total_files = 0
    for path in search_paths:
        if os.path.exists(path):
            files = os.listdir(path)
            json_files = [f for f in files if f.endswith('.json')]
            print(f"  > Folder '{path}': {len(json_files)} wallet files.")
            total_files += len(json_files)
        else:
            print(f"  > Folder '{path}': NOT FOUND.")
            
    # Also deep search?
    print(f"  > Total Wallet Files Found: {total_files}")
    return total_files

def audit_blockchain_holders():
    print("\n--- 2. AUDIT: BLOCKCHAIN DATA ---")
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT data FROM blocks")
        rows = c.fetchall()
        
        all_receivers = set()
        active_balances = {}
        
        print(f"  > Scanning {len(rows)} blocks...")
        
        for r in rows:
            try:
                b = json.loads(r[0])
                # Check Rewards
                for rew in b.get('rewards', []):
                    rcv = rew.get('receiver')
                    if rcv:
                        all_receivers.add(rcv)
                        active_balances[rcv] = active_balances.get(rcv, 0) + int(rew.get('amount', 0))
                
                # Check Transactions
                for tx in b.get('transactions', []):
                    rcv = tx.get('receiver')
                    sender = tx.get('sender')
                    amt = int(tx.get('amount', 0))
                    
                    if rcv:
                        all_receivers.add(rcv)
                        active_balances[rcv] = active_balances.get(rcv, 0) + amt
                    
                    if sender and sender != "SYSTEM":
                        active_balances[sender] = active_balances.get(sender, 0) - amt
                        # Sender must have received before, so already in set.
                        
            except Exception as e:
                pass
                
        # Count only those with positive balance
        valid_holders = [a for a, bal in active_balances.items() if bal > 0]
        
        print(f"  > Total Unique Addresses Seen (Ever): {len(all_receivers)}")
        print(f"  > Total Active Holders (Balance > 0): {len(valid_holders)}")
        
        # Check specific sample
        # print("  > Sample addresses:", valid_holders[:5])
        
        return len(valid_holders)
        
    except Exception as e:
        print(f"ERROR: {e}")
        return 0

def main():
    disk_count = audit_wallets_on_disk()
    chain_count = audit_blockchain_holders()
    
    print("\n--- 3. CONCLUSION ---")
    if disk_count > chain_count:
        gap = disk_count - chain_count
        print(f"[!] DISCREPANCY DETECTED: {gap} wallets exist on disk but have NEVER received a transaction.")
        print(f"    Possible Cause: Wallets were generated but Mining/Transfer script failed or hasn't run yet.")
    else:
        print("[OK] Data matches reasonably well.")

if __name__ == "__main__":
    main()
