import time
import os
import requests
import json
import random
from ecdsa import SigningKey, SECP256k1
from wallet import Transaction

NODE_URL = "http://localhost:5005"
WALLET_DIR = "wallets"

class SimpleWallet:
    def __init__(self, private_key):
        self.private_key = private_key
        self.public_key = self.private_key.verifying_key
        self.address = self.public_key.to_string().hex()

def load_wallets():
    wallets = []
    for i in range(1, 11):
        path = os.path.join(WALLET_DIR, f"p{i}.pem")
        if os.path.exists(path):
            with open(path, "r") as f:
                sk = SigningKey.from_pem(f.read())
            w = SimpleWallet(sk)
            wallets.append(w)
            print(f"[*] Loaded Wallet {i}: {w.address[:10]}...")
        else:
            print(f"[!] Warning: Wallet p{i}.pem not found at {path}")
    return wallets

def stress_test():
    wallets = load_wallets()
    if not wallets or len(wallets) < 10:
        print("[!] Error: Need 10 wallets to start stress test.")
        return

    print(f"\n[*] Starting Stress Test Loop (10s interval)...")
    
    iteration = 0
    while True:
        try:
            for i in range(10):
                sender = wallets[i]
                targets = [
                    wallets[(i + 1) % 10].address,
                    wallets[(i + 2) % 10].address,
                    wallets[(i + 3) % 10].address
                ]
                
                for target_addr in targets:
                    # Random amount between 1 and 10 HOME
                    amount = random.randint(1, 10) * 100_000_000
                    
                    tx = Transaction(
                        sender=sender.address,
                        receiver=target_addr,
                        amount=amount, 
                        fee=1_000_000, # Mandatory 0.01 fee
                        data={"type": "stress_test", "seq": iteration}
                    )
                    tx.sign(sender.private_key)
                    
                    try:
                        r = requests.post(f"{NODE_URL}/transactions/new", json=tx.to_dict(), timeout=2)
                        if r.status_code == 201:
                            print(f"[+] TX: {sender.address[:6]} -> {target_addr[:6]} OK")
                        else:
                            print(f"[-] TX: {sender.address[:6]} -> {target_addr[:6]} Failed: {r.text}")
                    except Exception as e:
                        print(f"[!] Request Error: {e}")
                    
                time.sleep(10) 
            
            iteration += 1
            print(f"[*] Cycle {iteration} completed.")
            
        except Exception as e:
            print(f"[!!] Loop Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    stress_test()
