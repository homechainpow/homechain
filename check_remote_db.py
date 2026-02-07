import sqlite3
import os

db_path = 'HomeChain/chain_v2.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT MAX(idx), SUM(balance), COUNT(*) FROM blocks, balances")
    # Wait, the cross join will be huge. Let's do separate.
    c.execute("SELECT MAX(idx) FROM blocks")
    max_idx = c.fetchone()[0]
    c.execute("SELECT SUM(balance) FROM balances")
    total_bal = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM balances")
    holders = c.fetchone()[0]
    print(f"Height: {max_idx}, Holders: {holders}, Supply Sum: {total_bal/100000000:.2f} HOME")
else:
    print(f"DB not found at {db_path}")
