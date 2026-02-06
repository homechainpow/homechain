
import os
import requests
import json

NODE_URL = "http://localhost:5005"
SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co/rest/v1"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"

def audit():
    # 1. Check Supabase Tx Count
    try:
        res = requests.get(f"{SB_URL}/transactions?select=id", headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Prefer": "count=exact"}, timeout=10)
        # Headers or JSON? Supabase count is usually in Range header or if select=count
        print(f"SUPABASE_TX_COUNT: {res.headers.get('Content-Range')}")
    except Exception as e:
        print(f"SB_ERROR: {e}")

    # 2. Check Blocks on Node (Full range scan for transactions)
    try:
        res = requests.get(f"{NODE_URL}/chain").json()
        blocks = res['chain']
        found = []
        for b in blocks:
            if len(b.get('transactions', [])) > 0:
                found.append((b['index'], len(b['transactions'])))
        
        print(f"BLOCKS_WITH_TXS: {found}")
    except Exception as e:
        print(f"NODE_ERROR: {e}")

if __name__ == "__main__":
    audit()
