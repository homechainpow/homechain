
import requests
import json

SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

def test_sync():
    # 1. Get stats
    print("[*] Testing Stats Get...")
    r = requests.get(f"{SB_URL}/rest/v1/stats?id=eq.1", headers=headers)
    print(f"Stats: {r.status_code} - {r.text}")
    
    # 2. Get blocks
    print("[*] Testing Blocks Get...")
    r = requests.get(f"{SB_URL}/rest/v1/blocks?order=id.desc&limit=1", headers=headers)
    print(f"Blocks: {r.status_code} - {r.text}")
    
    # 3. Post a dummy block if empty
    if r.status_code == 200 and not r.json():
        print("[*] Posting dummy block 0...")
        dummy = {"id": 0, "hash": "genesis", "validator": "SYSTEM", "timestamp": "2026-02-06 12:00:00"}
        r = requests.post(f"{SB_URL}/rest/v1/blocks", headers=headers, json=dummy)
        print(f"Post Result: {r.status_code} - {r.text}")

if __name__ == "__main__":
    test_sync()
