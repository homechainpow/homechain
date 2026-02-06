
import sqlite3
import json

DB_PATH = '/home/ubuntu/HomeChain/chain_v2.db'

def find():
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    c = conn.cursor()
    c.execute("SELECT data FROM blocks")
    for r in c.fetchall():
        try:
            b = json.loads(r[0])
            for rew in b.get('rewards', []):
                amt = int(rew.get('amount', 0))
                if amt > 10**16:
                    print(f"Crazy Reward in Block {b['index']}: {amt} to {rew.get('receiver')}")
            for tx in b.get('transactions', []):
                amt = int(tx.get('amount', 0))
                if amt > 10**16:
                    print(f"Crazy TX in Block {b['index']}: {amt} from {tx.get('sender')} to {tx.get('receiver')}")
        except: pass

if __name__ == "__main__":
    find()
