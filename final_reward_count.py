
import sqlite3
import json

DB_PATH = '/home/ubuntu/HomeChain/chain_v2.db'

def count():
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    c = conn.cursor()
    c.execute("SELECT data FROM blocks")
    total = 0
    all_rows = c.fetchall()
    for r in all_rows:
        try:
            b = json.loads(r[0])
            total += len(b.get('rewards', []))
        except: pass
    print(f"Blocks: {len(all_rows)}")
    print(f"Total Rewards: {total}")

if __name__ == "__main__":
    count()
