import os
import json
from ecdsa import SigningKey

# Paths
WALLETS_DIRS = [
    'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/wallets',
    'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/wallets_300'
]
OUTPUT_JSON = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/MASTER_WALLETS_MANIFEST.json'
OUTPUT_TXT = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/MASTER_WALLETS_LIST.txt'

def get_hex_from_pem(pem_path):
    try:
        with open(pem_path, 'r') as f:
            sk = SigningKey.from_pem(f.read())
            return sk.verifying_key.to_string().hex()
    except:
        return None

def consolidate_wallets():
    master_map = {} # HEX -> PEM filename
    
    for d in WALLETS_DIRS:
        if not os.path.exists(d):
            print(f"Skipping {d} (not found)")
            continue
        print(f"[*] Processing {d}...")
        for f in os.listdir(d):
            if f.endswith('.pem'):
                pem_path = os.path.join(d, f)
                hex_addr = get_hex_from_pem(pem_path)
                if hex_addr:
                    # If duplicate hex, we keep the first one found or longest filename?
                    # Let's just track all filenames for that hex
                    if hex_addr not in master_map:
                        master_map[hex_addr] = []
                    master_map[hex_addr].append(f"{f} (from {os.path.basename(d)})")

    print(f"[✓] Consistently identified {len(master_map)} unique HEX addresses.")
    
    # Save JSON
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(master_map, f, indent=4)
        
    # Save TXT (Sorted)
    with open(OUTPUT_TXT, 'w') as f:
        f.write("=== MASTER WALLET LIST (128-CHAR HEX) ===\n")
        f.write(f"Total Unique Wallets: {len(master_map)}\n\n")
        for addr in sorted(master_map.keys()):
            files = ", ".join(master_map[addr])
            f.write(f"{addr} | {files}\n")

    print(f"[*] Master manifest saved to {OUTPUT_JSON}")
    print(f"[*] Text list saved to {OUTPUT_TXT}")

if __name__ == "__main__":
    consolidate_wallets()
