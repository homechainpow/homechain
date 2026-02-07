
import sqlite3
import os

db_path = "/home/ubuntu/HomeChain/chain_v2.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Check if a 'nodes' table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nodes';")
    if cur.fetchone():
        cur.execute("SELECT * FROM nodes")
        rows = cur.fetchall()
        print(f"Total Nodes in DB: {len(rows)}")
        for r in rows:
            print(f"  - {r}")
    else:
        print("No 'nodes' table found in DB.")
    conn.close()
else:
    print("DB not found.")
