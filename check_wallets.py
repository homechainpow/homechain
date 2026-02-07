from ecdsa import SigningKey, SECP256k1
import os

def get_address_from_pem(pem_path):
    with open(pem_path, 'r') as f:
        pem_content = f.read()
        # Find the line that has the actual base64 data
        # simplified for this specific case
        sk = SigningKey.from_pem(pem_content)
        address = sk.verifying_key.to_string().hex()
        return address

miner_pem = r"C:\Users\Administrator\.gemini\antigravity\scratch\HomeChain\wallets\satya_main.pem"
print(f"Miner Address: {get_address_from_pem(miner_pem)}")

# List first 3 pX wallets just to be sure
for i in range(1, 4):
    p_pem = rf"C:\Users\Administrator\.gemini\antigravity\scratch\HomeChain\wallets\p{i}.pem"
    if os.path.exists(p_pem):
        print(f"p{i} Address: {get_address_from_pem(p_pem)}")
