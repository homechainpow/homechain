import requests
import sqlite3
import re
import json

# Config
DB_PATH = "C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/chain_v2.db"

with open('supabase_sync.py', 'r') as f:
    content = f.read()
    sb_url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    sb_key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}

def verify_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check Holders
    c.execute("SELECT COUNT(*) FROM balances WHERE balance > 0")
    local_holders = c.fetchone()[0]
    
    sb_holders_res = requests.get(f"{sb_url}/rest/v1/holders?select=count", headers={**headers, "Range": "0-0"}).json()
    sb_holders = sb_holders_res[0]['count']
    
    # Check Txs
    # We don't have a tx table in local SQLite (it's inside JSON in blocks table)
    # So we parse the last block's TXs
    c.execute("SELECT idx, data FROM blocks ORDER BY idx DESC LIMIT 1")
    last_block = c.fetchone()
    local_last_block_id = last_block[0]
    local_tx_count = len(json.loads(last_block[1]).get('transactions', []))
    
    sb_tx_res = requests.get(f"{sb_url}/rest/v1/transactions?block_id=eq.{local_last_block_id}&select=count", headers={**headers, "Range": "0-0"}).json()
    sb_tx_count = sb_tx_res[0]['count']
    
    print(f"Holders: Local={local_holders}, SB={sb_holders}")
    print(f"Last Block ({local_last_block_id}) TXs: Local={local_tx_count}, SB={sb_tx_count}")
    
    conn.close()

if __name__ == "__main__":
    verify_data()
