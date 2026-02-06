
import os
import requests
import json
from ecdsa import SigningKey

NODE_URL = "http://localhost:5005"
BASE_DIR = "/home/ubuntu/HomeChain"

def check_status():
    # 1. Miner 1 Balance
    try:
        with open(os.path.join(BASE_DIR, "wallets/p1.pem"), 'r') as f:
            sk = SigningKey.from_pem(f.read())
        addr = sk.verifying_key.to_string().hex()
        res = requests.get(f"{NODE_URL}/balance/{addr}").json()
        print(f"M1_ADDR: {addr}")
        print(f"M1_BALANCE: {res['balance']}")
    except Exception as e:
        print(f"M1_ERROR: {e}")

    # 2. Block 512 Content
    try:
        res = requests.get(f"{NODE_URL}/block/512").json()
        if 'error' in res:
             print(f"BLOCK_512: NOT FOUND")
        else:
            tx_count = len(res.get('transactions', []))
            print(f"BLOCK_512_TXS: {tx_count}")
            if tx_count > 0:
                print(f"FIRST_TX: {res['transactions'][0]['receiver']}")
    except Exception as e:
        print(f"BLOCK_512_ERROR: {e}")

    # 3. Node Stats
    try:
        res = requests.get(f"{NODE_URL}/chain").json()
        print(f"NODE_HEIGHT: {res['length']}")
        print(f"PENDING_TXS: {len(res.get('pending_transactions', []))}")
    except Exception as e:
        print(f"NODE_ERROR: {e}")

if __name__ == "__main__":
    check_status()
