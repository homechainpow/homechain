import sqlite3
import os

BACKUP_DB = 'C:/Users/Administrator/.gemini/antigravity/scratch/backups/release_2.10_pre_push/HomeChain/chain_v2.db'

def audit():
    conn = sqlite3.connect(BACKUP_DB)
    c = conn.cursor()
    c.execute("SELECT address, balance FROM balances WHERE address LIKE 'S_%' ORDER BY address ASC")
    rows = c.fetchall()
    print(f"Total S_xxx rows: {len(rows)}")
    for r in rows:
        print(f"  {r[0]}: {r[1]}")
    conn.close()

if __name__ == "__main__":
    audit()
