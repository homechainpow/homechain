
import sqlite3
import json

try:
    conn = sqlite3.connect('/home/ubuntu/HomeChain/chain_v2.db')
    cursor = conn.cursor()
    
    # Get Max Height
    cursor.execute("SELECT MAX(idx) FROM blocks")
    max_height = cursor.fetchone()[0]
    
    # Get Total Blocks
    cursor.execute("SELECT COUNT(*) FROM blocks")
    total_blocks = cursor.fetchone()[0]

    # Get Wallets (Wait, schema said wallets_schema is empty? Maybe it's a different table or key-value store?)
    # Let's check all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    
    # Check if there is a 'wallets' table and count it if it exists
    wallet_count = 0
    if 'wallets' in tables:
        cursor.execute("SELECT COUNT(*) FROM wallets")
        wallet_count = cursor.fetchone()[0]


    print(json.dumps({"max_height": max_height, "total_blocks": total_blocks, "tables": tables, "wallet_count": wallet_count}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
