import sqlite3
conn = sqlite3.connect('chain_v2.db')
c = conn.cursor()
for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    table = t[0]
    cols = [col[1] for col in c.execute(f"PRAGMA table_info({table})")]
    print(f"Table {table}: {cols}")
conn.close()
