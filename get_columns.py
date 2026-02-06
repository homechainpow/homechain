
import sqlite3
import json

try:
    conn = sqlite3.connect('/home/ubuntu/HomeChain/chain_v2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blocks LIMIT 1")
    columns = [description[0] for description in cursor.description]
    print(json.dumps(columns))
    
    # Also print the first row to see structure
    row = cursor.fetchone()
    # print(row) # Might be huge
except Exception as e:
    print(str(e))
