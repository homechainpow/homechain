
import sqlite3
import json

try:
    conn = sqlite3.connect('/home/ubuntu/HomeChain/chain_v2.db')
    cursor = conn.cursor()
    
    # Get Max Height
    cursor.execute("SELECT MAX(block_index) FROM blocks")
    max_height = cursor.fetchone()[0]
    
    # Get Wallet Count
    cursor.execute("SELECT COUNT(*) FROM wallets")
    wallet_count = cursor.fetchone()[0]
    
    print(json.dumps({"height": max_height, "wallets": wallet_count}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
