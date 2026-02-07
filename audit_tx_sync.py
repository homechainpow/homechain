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

def audit_txs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Check Blocks
    c.execute("SELECT idx, hash FROM blocks ORDER BY idx DESC LIMIT 5")
    local_blocks = c.fetchall()
    
    print("--- Recent Blocks Check ---")
    for idx, b_hash in local_blocks:
        sb_res = requests.get(f"{sb_url}/rest/v1/blocks?id=eq.{idx}&select=hash", headers=headers).json()
        sb_hash = sb_res[0]['hash'] if sb_res else "MISSING"
        match = "MATCH" if sb_hash == b_hash else "MISMATCH"
        print(f"Block #{idx}: Local={b_hash[:10]} | SB={sb_hash[:10]} | {match}")

    # 2. Check Transactions in Last 10 Blocks
    c.execute("SELECT idx, data FROM blocks ORDER BY idx DESC LIMIT 10")
    recent_blocks_data = c.fetchall()
    
    print("\n--- Transaction Count Audit ---")
    for idx, data_json in recent_blocks_data:
        data = json.loads(data_json)
        local_txs = len(data.get('transactions', []))
        local_rews = len(data.get('rewards', []))
        
        sb_tx_res = requests.get(f"{sb_url}/rest/v1/transactions?block_id=eq.{idx}&select=count", headers={**headers, "Range": "0-0"}).json()
        sb_tx_count = sb_tx_res[0]['count'] if sb_tx_res else 0
        
        sb_rew_res = requests.get(f"{sb_url}/rest/v1/rewards?block_id=eq.{idx}&select=count", headers={**headers, "Range": "0-0"}).json()
        sb_rew_count = sb_rew_res[0]['count'] if sb_rew_res else 0
        
        tx_status = "OK" if local_txs == sb_tx_count else "!! MISSING !!"
        print(f"Block #{idx}: Local TXs={local_txs}, SB TXs={sb_tx_count} | {tx_status}")

    conn.close()

if __name__ == "__main__":
    audit_txs()
