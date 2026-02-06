
import os
import requests
import json
import time
from ecdsa import SigningKey, SECP256k1
from wallet import Transaction

NODE_URL = "http://localhost:5005"
SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"

BASE_DIR = "/home/ubuntu/HomeChain"
WALLET_PATH = os.path.join(BASE_DIR, "wallets/p1.pem")

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

def load_wallet_key(path):
    with open(path, "r") as f:
        return SigningKey.from_pem(f.read())

def get_addr(sk):
    return sk.verifying_key.to_string().hex()

def run_airdrop():
    print("=== HomeChain Mass Airdrop: 1 HOME to all Holders ===")
    
    # 1. Load Sender (Miner 1)
    if not os.path.exists(WALLET_PATH):
        print(f"[!] Error: Wallet not found at {WALLET_PATH}")
        return
    sk = load_wallet_key(WALLET_PATH)
    sender = get_addr(sk)
    print(f"[*] Sender Address: {sender}")
    
    # 2. Fetch Holders from Supabase
    print("[*] Fetching holders from Supabase...")
    try:
        # Fetching all holders (max 1000)
        res = requests.get(f"{SB_URL}/rest/v1/holders?select=address", headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"[!] SB Error: {res.status_code} - {res.text}")
            return
        holders = [h['address'] for h in res.json()]
        print(f"[*] Found {len(holders)} unique addresses.")
    except Exception as e:
        print(f"[!] Fetch Exception: {e}")
        return

    # 3. Filter out sender and duplicates
    recipients = list(set([h for h in holders if h != sender]))
    print(f"[*] Ready to airdrop to {len(recipients)} recipients.")

    # 4. Execute transfers (1 HOME = 100,000,000 Satoshis)
    amount = 100_000_000 
    success_count = 0
    fail_count = 0

    for i, target in enumerate(recipients, 1):
        print(f"[{i}/{len(recipients)}] Sending 1 HOME to {target[:10]}...")
        
        tx = Transaction(sender, target, amount)
        tx.sign(sk)
        
        try:
            res = requests.post(f"{NODE_URL}/transactions/new", json=tx.to_dict(), timeout=10)
            if res.status_code == 201:
                success_count += 1
            else:
                print(f"    [!] Failed: {res.status_code} - {res.text}")
                fail_count += 1
        except Exception as e:
            print(f"    [!] Error: {e}")
            fail_count += 1
        
        # Throttling to keep node and sync healthy
        time.sleep(0.3)

    print("\n=== Airdrop Summary ===")
    print(f"[+] Successfully sent: {success_count}")
    print(f"[-] Failed: {fail_count}")
    print("[*] Check the scanner for real-time updates!")

if __name__ == "__main__":
    run_airdrop()
