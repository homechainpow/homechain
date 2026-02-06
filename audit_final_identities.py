
import sys
import os
from ecdsa import SigningKey

# Add local dir to path
sys.path.append('.')

from blockchain import Blockchain

def audit():
    print("=== Final Identity & Balance Audit ===")
    bc = Blockchain()
    
    wallet_dir = "wallets"
    for i in range(1, 11):
        path = os.path.join(wallet_dir, f"p{i}.pem")
        if os.path.exists(path):
            with open(path, "r") as f:
                sk = SigningKey.from_pem(f.read())
                addr = sk.verifying_key.to_string().hex()
                bal = bc.balances.get(addr, 0)
                print(f"[*] Miner {i}: {addr} | Balance: {bal} ({bal/100_000_000:.2f} HOME)")

if __name__ == "__main__":
    audit()
