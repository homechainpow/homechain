
import sqlite3
import os

db_path = "/home/ubuntu/HomeChain/chain_v2.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT count(*) FROM blocks")
    count = c.fetchone()[0]
    print(f"DB_COUNT:{count}")
else:
    print("DB_NOT_FOUND")
