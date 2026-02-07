import sqlite3
from ecdsa import SigningKey
import os
import re

# --- SETTINGS ---
DB_PATH = 'chain_v2.db'
WALLETS_DIR = 'wallets_300'
SATYA_MAIN_FULL = "aa0ba2e22c9cd4a6bc50b5cb993a87ad9ff39e6c249460378799bb93216ed69d44a16d905db4b27c6305b19317420f4f2d6d66ab06e77b1ad5796646b212364c"
SATYA_TRUNCATED = "aa0ba2e22c9cd4a6bc50b5c18bab9685ed69f9876e6b093390c7511d433644d96796646b212364c6e77b1ad57"

def get_wallet_address(p_num):
    pem_path = os.path.join(WALLETS_DIR, f"p{p_num}.pem")
    if not os.path.exists(pem_path):
        return None
    with open(pem_path, 'r') as f:
        try:
            sk = SigningKey.from_pem(f.read())
            return sk.verifying_key.to_string().hex()
        except Exception as e:
            print(f"  [!] Error reading p{p_num}.pem: {e}")
            return None

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Clean SYSTEM and GENESIS (trash labels)
    # Move their balances to Satya Main (the dev wallet) to keep total supply accurate
    print("[*] Cleaning SYSTEM, GENESIS, and other trash labels...")
    trash_labels = ['SYSTEM', 'GENESIS', 'GENESIS_REWARD', 'MINE_POOL', 'M1', 'M2', 'M3']
    for label in trash_labels:
        c.execute("SELECT balance FROM balances WHERE address = ?", (label,))
        row = c.fetchone()
        if row:
            bal = row[0]
            print(f"  [-] Moving {label} balance ({bal/10**8:.2f}) to Satya Main...")
            c.execute("UPDATE balances SET balance = balance + ? WHERE address = ?", (bal, SATYA_MAIN_FULL))
            c.execute("DELETE FROM balances WHERE address = ?", (label,))

    # 2. Migrate Satya Truncated -> Full
    c.execute("SELECT balance FROM balances WHERE address = ?", (SATYA_TRUNCATED,))
    row = c.fetchone()
    if row:
        trunc_bal = row[0]
        print(f"[*] Migrating Satya Truncated ({trunc_bal/10**8:.2f}) to Full Address...")
        c.execute("UPDATE balances SET balance = balance + ? WHERE address = ?", (trunc_bal, SATYA_MAIN_FULL))
        if c.rowcount == 0:
            c.execute("INSERT OR REPLACE INTO balances (address, balance) VALUES (?, ?)", (SATYA_MAIN_FULL, trunc_bal))
        c.execute("DELETE FROM balances WHERE address = ?", (SATYA_TRUNCATED,))
    
    # 3. Migrate ALL S_xxx labels found in DB
    print("[*] Auditing and Migrating ALL S_xxx labels...")
    c.execute("SELECT address, balance FROM balances WHERE address LIKE 'S_%'")
    s_labels = c.fetchall()
    print(f"  Found {len(s_labels)} S_xxx labels.")
    
    migrated_count = 0
    for label, bal in s_labels:
        # Match S_ followed by numbers
        match = re.search(r'S_(\d+)', label)
        if match:
            num = int(match.group(1))
            # Logic: S_901 is p1, S_902 is p2... S_1101 is p201?
            # User previously said S_901..S_999 = p1..p99
            # So p_num = num - 900
            p_num = num - 900
            if p_num > 0:
                hex_addr = get_wallet_address(p_num)
                if hex_addr:
                    print(f"  [+] {label} ({bal/10**8:.2f}) -> {hex_addr[:16]}...")
                    c.execute("INSERT INTO balances (address, balance) SELECT ?, 0 WHERE NOT EXISTS (SELECT 1 FROM balances WHERE address = ?)", (hex_addr, hex_addr))
                    c.execute("UPDATE balances SET balance = balance + ? WHERE address = ?", (bal, hex_addr))
                    c.execute("DELETE FROM balances WHERE address = ?", (label,))
                    migrated_count += 1
                else:
                    print(f"  [!] No wallet for {label} (p{p_num}.pem missing)")
            else:
                print(f"  [!] Skipping {label} (number too low for mapping)")
        else:
            print(f"  [!] Invalid label format: {label}")

    conn.commit()
    
    # 4. Final Cleanup: Delete any address that is not a 128-char hex
    c.execute("SELECT address, balance FROM balances")
    all_holders = c.fetchall()
    for addr, bal in all_holders:
        if len(addr) != 128:
            print(f"  [!] Deleting lingering non-HEX address: {addr} ({bal/10**8:.2f})")
            c.execute("DELETE FROM balances WHERE address = ?", (addr,))

    conn.commit()
    
    c.execute("SELECT SUM(balance) FROM balances")
    new_total = c.fetchone()[0] or 0
    print(f"\n[✓] Migration Complete. Migrated {migrated_count} labels.")
    print(f"[✓] New Total Supply in DB: {new_total/10**8:.2f} HOME")
    
    conn.close()

if __name__ == "__main__":
    migrate()
