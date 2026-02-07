import sqlite3
import os
from ecdsa import SigningKey

# Paths
BACKUP_DB = 'backups/release_2.10_pre_push/HomeChain/chain_v2.db'
WALLETS_DIR = 'wallets'

def get_hex_from_pem(pem_path):
    if not os.path.exists(pem_path):
        return None
    with open(pem_path, 'r') as f:
        sk = SigningKey.from_pem(f.read())
        return sk.verifying_key.to_string().hex()

def recover_and_map():
    if not os.path.exists(BACKUP_DB):
        print(f"Error: {BACKUP_DB} not found.")
        return

    conn = sqlite3.connect(BACKUP_DB)
    c = conn.cursor()
    
    # 1. Fetch S_xxx balances
    print("[*] Fetching balances from backup...")
    c.execute("SELECT address, balance FROM balances WHERE address LIKE 'S_%'")
    s_balances = c.fetchall()
    print(f"    Found {len(s_balances)} S_xxx records.")

    mapping = {}
    for label, bal in s_balances:
        # Expected format: S_901, S_902, etc.
        try:
            num = int(label.split('_')[1])
            if num >= 901:
                p_num = num - 900
                pem_file = f"p{p_num}.pem"
                pem_path = os.path.join(WALLETS_DIR, pem_file)
                hex_addr = get_hex_from_pem(pem_path)
                if hex_addr:
                    mapping[label] = {
                        "hex": hex_addr,
                        "balance": bal,
                        "p_num": p_num
                    }
        except Exception as e:
            print(f"    [!] Error mapping {label}: {e}")

    # 2. Add System/Genesis/Truncated to mapping for complete recovery if needed
    # (Actually user just wants the 101 wallets fixed)
    
    print(f"\n[✓] Mapped {len(mapping)} wallets.")
    for label, info in list(mapping.items())[:10]:
        print(f"    {label} -> {info['hex'][:16]}... | Balance: {info['balance']/10**8:.2f} HOME")

    # Save mapping to a JSON for the sync script to use
    import json
    with open('recovered_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=4)
    print("\n[*] Mapping saved to recovered_mapping.json")

    conn.close()

if __name__ == "__main__":
    recover_and_map()
