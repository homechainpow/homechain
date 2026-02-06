
import sqlite3
import json

DB_PATH = '/home/ubuntu/HomeChain/chain_v2.db'

def check():
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    c = conn.cursor()
    c.execute("SELECT data FROM blocks WHERE idx=0")
    b = json.loads(c.fetchone()[0])
    print("GENESIS REWARDS:")
    print(json.dumps(b.get('rewards', []), indent=2))
    print("GENESIS TXS:")
    print(json.dumps(b.get('transactions', []), indent=2))

if __name__ == "__main__":
    check()
