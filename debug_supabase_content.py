
import requests
import json

SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

def check():
    print("--- Supabase Data Audit ---")
    
    # Check Blocks
    r = requests.get(f"{SB_URL}/rest/v1/blocks?select=id,hash,timestamp&order=id.desc&limit=5", headers=headers)
    print(f"Blocks (Latest 5): {r.json()}")
    
    # Check Stats
    r = requests.get(f"{SB_URL}/rest/v1/stats?id=eq.1", headers=headers)
    print(f"Stats: {r.json()}")
    
    # Check Transactions count
    r = requests.get(f"{SB_URL}/rest/v1/transactions?select=count", headers={**headers, "Prefer": "count=exact"})
    print(f"Total Txs: {r.headers.get('Content-Range')}")

if __name__ == "__main__":
    check()
