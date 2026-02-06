
import sqlite3
import json

try:
    conn = sqlite3.connect('/home/ubuntu/HomeChain/chain_v2.db')
    cursor = conn.cursor()
    
    # Get Schema
    cursor.execute("PRAGMA table_info(blocks)")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Get Wallet Table Schema
    cursor.execute("PRAGMA table_info(wallets)")
    w_columns = [row[1] for row in cursor.fetchall()]

    print(json.dumps({"blocks_schema": columns, "wallets_schema": w_columns}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
