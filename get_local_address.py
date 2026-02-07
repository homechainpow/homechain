
from ecdsa import SigningKey, SECP256k1
import sys
import os

class SimpleWallet:
    def __init__(self, private_key):
        self.private_key = private_key
        self.public_key = self.private_key.verifying_key
        self.address = self.public_key.to_string().hex()

pem_path = r"C:\Users\Administrator\Downloads\miner_155.pem"

if not os.path.exists(pem_path):
    print(f"Error: PEM file not found at {pem_path}")
    sys.exit(1)

try:
    with open(pem_path, 'r') as f:
        sk = SigningKey.from_pem(f.read())
    
    wallet = SimpleWallet(sk)
    print(f"Address: {wallet.address}")

except Exception as e:
    print(f"Error reading PEM: {e}")
