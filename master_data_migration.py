import sqlite3
from ecdsa import SigningKey
import os

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
        sk = SigningKey.from_pem(f.read())
        return sk.verifying_key.to_string().hex()

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Migrate Satya Truncated -> Full
    c.execute("SELECT balance FROM balances WHERE address = ?", (SATYA_TRUNCATED,))
    row = c.fetchone()
    if row:
        trunc_bal = row[0]
        print(f"[*] Migrating Satya Truncated ({trunc_bal/10**8:.2f}) to Full Address...")
        c.execute("UPDATE balances SET balance = balance + ? WHERE address = ?", (trunc_bal, SATYA_MAIN_FULL))
        # If full doesn't exist, this might do nothing. Let's use UPSERT logic instead.
        if c.rowcount == 0:
            c.execute("INSERT OR REPLACE INTO balances (address, balance) VALUES (?, ?)", (SATYA_MAIN_FULL, trunc_bal))
        c.execute("DELETE FROM balances WHERE address = ?", (SATYA_TRUNCATED,))
    
    # 2. Migrate S_901...S_999 -> p1...p99
    print("[*] Migrating S_901...S_999 labels to pX.pem addresses...")
    migrated_count = 0
    for i in range(1, 100):
        label = f"S_{900 + i}"
        c.execute("SELECT balance FROM balances WHERE address = ?", (label,))
        row = c.fetchone()
        if row:
            bal = row[0]
            hex_addr = get_wallet_address(i)
            if hex_addr:
                print(f"  [+] {label} ({bal/10**8:.2f}) -> {hex_addr[:16]}...")
                c.execute("INSERT INTO balances (address, balance) SELECT ?, 0 WHERE NOT EXISTS (SELECT 1 FROM balances WHERE address = ?)", (hex_addr, hex_addr))
                c.execute("UPDATE balances SET balance = balance + ? WHERE address = ?", (bal, hex_addr))
                c.execute("DELETE FROM balances WHERE address = ?", (label,))
                migrated_count += 1
            else:
                print(f"  [!] No wallet for {label} (p{i}.pem missing)")

    conn.commit()
    
    # 3. Double Check Totals
    c.execute("SELECT SUM(balance) FROM balances")
    new_total = c.fetchone()[0] or 0
    print(f"\n[✓] Migration Complete. Migrated {migrated_count} labels.")
    print(f"[✓] New Total Supply: {new_total/10**8:.2f} HOME")
    
    conn.close()

if __name__ == "__main__":
    migrate()
