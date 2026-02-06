
import os
import requests
import json
import time
import binascii
from ecdsa import SigningKey, SECP256k1
from wallet import Transaction

NODE_URL = "http://localhost:5005"
# Use absolute path for server
BASE_DIR = "/home/ubuntu/HomeChain"
WALLET_DIR = os.path.join(BASE_DIR, "wallets")

def load_wallet_key(path):
    with open(path, "r") as f:
        return SigningKey.from_pem(f.read())

def get_addr(sk):
    return sk.verifying_key.to_string().hex()

def run_test():
    print("=== HomeChain Transfer Test v3: 11 Coins to 9 Miners ===")
    
    # 1. Load Miner 1 (Source)
    m1_path = os.path.join(WALLET_DIR, "p1.pem")
    if not os.path.exists(m1_path):
        print(f"[!] Error: Miner 1 PEM not found at {m1_path}")
        return
        
    m1_sk = load_wallet_key(m1_path)
    sender = get_addr(m1_sk)
    print(f"[*] Source (Miner 1): {sender}")
    
    # 2. Collect Recipients (Miner 2 to 10)
    recipients = []
    for i in range(2, 11):
        path = os.path.join(WALLET_DIR, f"p{i}.pem")
        if not os.path.exists(path):
            print(f"[!] Warning: Miner {i} PEM not found at {path}")
            continue
        sk = load_wallet_key(path)
        addr = get_addr(sk)
        recipients.append(addr)
        print(f"[*] Target (Miner {i}): {addr}")

    # 3. Send 11 coins (1,100,000,000 satoshis) to each
    amount = 11 * 100_000_000
    
    for i, target in enumerate(recipients, 2):
        print(f"[*] Sending 11 HOME to Miner {i} ({target})...")
        
        # Create Transaction object
        tx = Transaction(sender, target, amount)
        
        # Sign manually
        tx.sign(m1_sk)
        
        # Post to Node
        payload = tx.to_dict()
        try:
            res = requests.post(f"{NODE_URL}/transactions/new", json=payload, timeout=10)
            if res.status_code == 201:
                print(f"[+] Success: {res.json()['message']}")
            else:
                print(f"[!] Failed: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"[!] Error: {e}")
        
        time.sleep(1.0) # Delay for potential block inclusion

if __name__ == "__main__":
    run_test()
