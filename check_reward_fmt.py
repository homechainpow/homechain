
import sqlite3
import json

DB_PATH = '/home/ubuntu/HomeChain/chain_v2.db'

def check():
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    c = conn.cursor()
    c.execute("SELECT data FROM blocks ORDER BY idx ASC LIMIT 5")
    for r in c.fetchall():
        b = json.loads(r[0])
        print(f"Block {b['index']} rewards count: {len(b.get('rewards', []))}")
        if b.get('rewards'):
            print(f"  Sample reward: {b['rewards'][0]}")

if __name__ == "__main__":
    check()
