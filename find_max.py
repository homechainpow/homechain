
import sqlite3
import json

DB_PATH = '/home/ubuntu/HomeChain/chain_v2.db'

def find_max():
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    c = conn.cursor()
    c.execute("SELECT data FROM blocks")
    max_amt = 0
    max_loc = ""
    for r in c.fetchall():
        try:
            b = json.loads(r[0])
            for rew in b.get('rewards', []):
                amt = int(rew.get('amount', 0))
                if amt > max_amt:
                    max_amt = amt
                    max_loc = f"Block {b['index']} reward"
            for tx in b.get('transactions', []):
                amt = int(tx.get('amount', 0))
                if amt > max_amt:
                    max_amt = amt
                    max_loc = f"Block {b['index']} tx"
        except: pass
    print(f"Max Amount: {max_amt} found at {max_loc}")

if __name__ == "__main__":
    find_max()
