import requests
import sqlite3
import re
import json

# Config
NODE_URL = "http://localhost:5005"
DB_PATH = "C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/chain_v2.db"

with open('supabase_sync.py', 'r') as f:
    content = f.read()
    sb_url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    sb_key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}

def check_discrepancy():
    print("=== Sync Discrepancy Report ===")
    
    # 1. Local Height (SQLite)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT MAX(idx) FROM blocks")
    local_height = c.fetchone()[0]
    conn.close()
    print(f"Local Height (SQLite): {local_height}")

    # 2. Node Height (API)
    try:
        node_res = requests.get(f"{NODE_URL}/chain", timeout=5).json()
        node_height = node_res.get('height', 0)
        print(f"Node Height (API): {node_height}")
    except Exception as e:
        print(f"Node API Error: {e}")
        node_height = 0

    # 3. Supabase Height
    try:
        sb_res = requests.get(f"{sb_url}/rest/v1/blocks?select=id&order=id.desc&limit=1", headers=headers).json()
        sb_height = sb_res[0]['id'] if sb_res else 0
        print(f"Supabase Height: {sb_height}")
    except Exception as e:
        print(f"Supabase Error: {e}")
        sb_height = 0

    # 4. Compare Last TX
    print("\n--- Last Transaction Check ---")
    try:
        sb_txs = requests.get(f"{sb_url}/rest/v1/transactions?select=id,timestamp&order=id.desc&limit=1", headers=headers).json()
        print(f"Last Supabase TX: {sb_txs[0] if sb_txs else 'None'}")
    except:
        pass

    if sb_height < local_height:
        print(f"\n[!] ALERT: Supabase is lagging by {local_height - sb_height} blocks.")
    else:
        print("\n[✓] Height is synchronized.")

if __name__ == "__main__":
    check_discrepancy()
