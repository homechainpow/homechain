import sqlite3
import json

conn = sqlite3.connect('chain_v2.db')
c = conn.cursor()
c.execute("SELECT idx, data FROM blocks WHERE data LIKE '%S_%' ORDER BY idx ASC LIMIT 1")
row = c.fetchone()
if row:
    print(f"First block with S_ label: {row[0]}")
    print(f"Data: {row[1][:200]}...")
else:
    print("No S_ labels found in blocks table data.")
conn.close()
