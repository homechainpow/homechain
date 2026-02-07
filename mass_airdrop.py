import requests
import time
import os
import json
from ecdsa import SigningKey, SECP256k1

NODE_URL = "http://localhost:5005"
WALLETS_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\HomeChain\wallets"
AIRDROP_AMOUNT = 1000 * 100_000_000 # 1,000 $HOME

def get_address_from_pem(pem_path):
    try:
        with open(pem_path, 'r') as f:
            pem_content = f.read()
            sk = SigningKey.from_pem(pem_content)
            address = sk.verifying_key.to_string().hex()
            return address
    except Exception as e:
        print(f"Error reading {pem_path}: {e}")
        return None

def submit_airdrop(receiver):
    tx = {
        "sender": "SYSTEM",
        "receiver": receiver,
        "amount": AIRDROP_AMOUNT,
        "fee": 0,
        "data": {"type": "airdrop"},
        "timestamp": time.time(),
        "signature": "SYSTEM_SIG" # SYSTEM doesn't need real sig
    }
    try:
        resp = requests.post(f"{NODE_URL}/transactions/new", json=tx)
        return resp.status_code == 201, resp.text
    except Exception as e:
        return False, str(e)

def run_airdrop():
    print(f"🚀 Starting Mass Airdrop to 100 wallets...")
    count = 0
    for i in range(1, 101):
        pem_file = os.path.join(WALLETS_DIR, f"p{i}.pem")
        if os.path.exists(pem_file):
            address = get_address_from_pem(pem_file)
            if address:
                success, msg = submit_airdrop(address)
                if success:
                    count += 1
                    print(f"✅ [{count}/100] Airdropped to p{i}: {address[:16]}...")
                else:
                    print(f"❌ Failed airdrop to p{i}: {msg}")
        else:
            print(f"⚠️ Warning: {pem_file} not found")
        
        # small delay to not overwhelm mempool
        if i % 10 == 0:
            time.sleep(0.5)

    print(f"\n📊 Airdrop Complete! Total successful: {count}/100")

if __name__ == "__main__":
    run_airdrop()
