import sqlite3
import os
import json
from ecdsa import SigningKey

# Paths
BACKUP_DB = 'C:/Users/Administrator/.gemini/antigravity/scratch/backups/release_2.10_pre_push/HomeChain/chain_v2.db'
WALLETS_DIR = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/wallets_300'

def get_hex_from_pem(pem_path):
    if not os.path.exists(pem_path):
        return None
    try:
        with open(pem_path, 'r') as f:
            sk = SigningKey.from_pem(f.read())
            return sk.verifying_key.to_string().hex()
    except:
        return None

def generate_mapping():
    conn = sqlite3.connect(BACKUP_DB)
    c = conn.cursor()
    c.execute("SELECT address, balance FROM balances WHERE address LIKE 'S_%'")
    rows = c.fetchall()
    
    mapping = {}
    for label, bal in rows:
        try:
            num = int(label.split('_')[1])
            # Mapping Logic
            if 901 <= num <= 1000:
                p_num = num - 900
            elif num >= 1101:
                p_num = num - 900 # If S_1101 is p201
            else:
                print(f"  [?] Unknown label range: {label}")
                continue
                
            pem_path = os.path.join(WALLETS_DIR, f"p{p_num}.pem")
            hex_addr = get_hex_from_pem(pem_path)
            
            if hex_addr:
                mapping[label] = {
                    "hex": hex_addr,
                    "balance": int(bal)
                }
            else:
                print(f"  [!] Missing PEM for {label} (p{p_num}.pem)")
        except:
            print(f"  [!] Failed to parse {label}")

    print(f"\n[✓] Generated mapping for {len(mapping)} wallets.")
    with open('final_recovery_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=4)
    
    conn.close()

if __name__ == "__main__":
    generate_mapping()
