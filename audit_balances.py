
import os
import requests
import json
from ecdsa import SigningKey

NODE_URL = "http://localhost:5005"
BASE_DIR = "/home/ubuntu/HomeChain"

def audit():
    # 1. Get all validator addresses from chain
    try:
        res = requests.get(f"{NODE_URL}/chain").json()
        height = res['length']
        validators = res.get('validators', [])
        print(f"HEIGHT: {height}")
        print(f"VALIDATORS_IN_STATE: {validators}")

        # 2. Check balance of each known validator
        balances = {}
        for v in validators:
            b_res = requests.get(f"{NODE_URL}/balance/{v}").json()
            balances[v] = b_res['balance']
        
        # Sort and print
        sorted_bal = sorted(balances.items(), key=lambda x: x[1], reverse=True)
        print("TOP HOLDERS ON NODE:")
        for addr, bal in sorted_bal[:10]:
            print(f"  {addr}: {bal}")

        # 3. Check M1 specifically again
        with open(os.path.join(BASE_DIR, "wallets/p1.pem"), 'r') as f:
            sk = SigningKey.from_pem(f.read())
        m1_addr = sk.verifying_key.to_string().hex()
        m1_bal = balances.get(m1_addr, "NOT_IN_VALIDATORS")
        if m1_bal == "NOT_IN_VALIDATORS":
             m1_res = requests.get(f"{NODE_URL}/balance/{m1_addr}").json()
             m1_bal = m1_res['balance']
        print(f"MINER_1 ({m1_addr}) BALANCE: {m1_bal}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    audit()
