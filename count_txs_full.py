
import sqlite3
import json

DB_PATH = '/home/ubuntu/HomeChain/chain_v2.db'

def count_txs():
    try:
        conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
        c = conn.cursor()
        c.execute("SELECT data FROM blocks")
        total_txs = 0
        total_rewards = 0
        rows = c.fetchall()
        for r in rows:
            try:
                b = json.loads(r[0])
                total_txs += len(b.get('transactions', []))
                total_rewards += len(b.get('rewards', []))
            except:
                pass
        print(f"Blocks in DB: {len(rows)}")
        print(f"Transactions in DB: {total_txs}")
        print(f"Rewards in DB: {total_rewards}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_txs()
