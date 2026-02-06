
import sqlite3

DB_PATH = '/home/ubuntu/HomeChain/chain_v2.db'

def check():
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    print(f"Tables: {tables}")
    
    for t in tables:
        try:
            cnt = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
            print(f"{t}: {cnt}")
        except Exception as e:
            print(f"{t}: Error {e}")

if __name__ == "__main__":
    check()
