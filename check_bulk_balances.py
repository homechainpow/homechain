
import sqlite3
import json
import requests
import sys

# Assume DB is at standard location
DB_PATH = '/home/ubuntu/HomeChain/chain_v2.db'
ADDRESS_FILE = '/home/ubuntu/HomeChain/vip_wealth_addresses.txt'
API_URL = "http://localhost:5005"

def get_balance_from_api(addr):
    try:
        res = requests.get(f"{API_URL}/balance/{addr}", timeout=2)
        if res.status_code == 200:
            return res.json().get('balance', 0)
    except:
        return 0
    return 0

def main():
    if not os.path.exists(ADDRESS_FILE):
        print("Address file not found.")
        return

    with open(ADDRESS_FILE, 'r') as f:
        addresses = [line.strip() for line in f if line.strip()]

    print(f"Checking {len(addresses)} addresses against Node...")
    
    found_count = 0
    total_balance = 0
    
    for i, addr in enumerate(addresses):
        bal = get_balance_from_api(addr)
        if bal > 0:
            found_count += 1
            total_balance += bal
            # print(f"  [+] {addr}: {bal}")
        
        if i % 50 == 0:
            print(f"  ... checked {i}/{len(addresses)} ...")
            
    print("-" * 30)
    print(f"Total Verified VIP Wallets: {len(addresses)}")
    print(f"Total Active (Balance > 0): {found_count}")
    print(f"Total Wealth: {total_balance}")
    print("-" * 30)

if __name__ == "__main__":
    import os
    main()
