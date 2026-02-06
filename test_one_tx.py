
import os
import requests
import json
import time
from ecdsa import SigningKey, SECP256k1
from wallet import Transaction

NODE_URL = "http://localhost:5005"
BASE_DIR = "/home/ubuntu/HomeChain"
WALLET_DIR = os.path.join(BASE_DIR, "wallets")

def load_wallet_key(path):
    with open(path, "r") as f:
        return SigningKey.from_pem(f.read())

def get_addr(sk):
    return sk.verifying_key.to_string().hex()

def run_test():
    print("=== HomeChain Single Tx Persistence Test ===")
    
    # 1. Load Miner 1 (Source)
    m1_path = os.path.join(WALLET_DIR, "p1.pem")
    m1_sk = load_wallet_key(m1_path)
    sender = get_addr(m1_sk)
    
    # 2. Load Miner 2 (Target)
    m2_path = os.path.join(WALLET_DIR, "p2.pem")
    m2_sk = load_wallet_key(m2_path)
    target = get_addr(m2_sk)

    print(f"[*] Sender: {sender[:10]}... | Target: {target[:10]}...")

    # 3. Send 10 HOME (1,000,000,000 satoshis)
    amount = 10 * 100_000_000
    tx = Transaction(sender, target, amount)
    tx.sign(m1_sk)
    
    res = requests.post(f"{NODE_URL}/transactions/new", json=tx.to_dict(), timeout=10)
    if res.status_code == 201:
        print(f"[+] Success: Transaction added to mempool.")
    else:
        print(f"[!] Failed: {res.status_code} - {res.text}")
        return

    # 4. Check Mempool
    time.sleep(1)
    res = requests.get(f"{NODE_URL}/chain").json()
    pending = res.get('pending_transactions', [])
    print(f"[*] PENDING COUNT: {len(pending)}")
    if len(pending) > 0:
        print(f"[+] Verification: Transaction IS in mempool.")
    else:
        print(f"[-] Verification FAILED: Mempool is empty.")

if __name__ == "__main__":
    run_test()
