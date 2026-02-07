import os
import json
from ecdsa import SigningKey

# Paths
WALLETS_DIR = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/wallets'
OUTPUT_MANIFEST = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/wallets_manifest.json'

def get_hex_from_pem(pem_path):
    try:
        with open(pem_path, 'r') as f:
            sk = SigningKey.from_pem(f.read())
            return sk.verifying_key.to_string().hex()
    except Exception as e:
        print(f"Error reading {pem_path}: {e}")
        return None

def generate_manifest():
    if not os.path.exists(WALLETS_DIR):
        print(f"Error: {WALLETS_DIR} not found.")
        return

    pem_files = [f for f in os.listdir(WALLETS_DIR) if f.endswith('.pem')]
    print(f"[*] Found {len(pem_files)} PEM files.")

    manifest = []
    for pem_file in pem_files:
        pem_path = os.path.join(WALLETS_DIR, pem_file)
        hex_addr = get_hex_from_pem(pem_path)
        if hex_addr:
            manifest.append({
                "file": pem_file,
                "address": hex_addr
            })

    print(f"[✓] Derived {len(manifest)} valid HEX addresses.")
    
    with open(OUTPUT_MANIFEST, 'w') as f:
        json.dump(manifest, f, indent=4)
    
    print(f"[*] Manifest saved to {OUTPUT_MANIFEST}")

if __name__ == "__main__":
    generate_manifest()
