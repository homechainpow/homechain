import sqlite3
conn = sqlite3.connect('chain_v2.db')
c = conn.cursor()
for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    table = t[0]
    cursor2 = conn.cursor()
    cols = [col[1] for col in cursor2.execute(f"PRAGMA table_info({table})")]
    print(f"--- {table} ---")
    print(", ".join(cols))
conn.close()
