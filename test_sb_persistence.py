import requests
import json

SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

def test():
    print("[*] Testing Supabase Connection...")
    
    # 1. Check Blocks
    res = requests.get(f"{SB_URL}/rest/v1/blocks?limit=5", headers=headers)
    print(f"Blocks ({res.status_code}): {res.text}")
    
    # 2. Check Holders
    res = requests.get(f"{SB_URL}/rest/v1/holders?limit=5&select=address,balance", headers=headers)
    print(f"Holders ({res.status_code}): {res.text}")
    
    # 3. Check Stats
    res = requests.get(f"{SB_URL}/rest/v1/stats?id=eq.1", headers=headers)
    print(f"Stats ({res.status_code}): {res.text}")

    # 4. Try manual insert to a test table or just blocks
    test_block = {"id": 8888, "hash": "test_persistence", "validator": "ai_test", "timestamp": "2026-02-06T17:00:00Z"}
    res = requests.post(f"{SB_URL}/rest/v1/blocks", headers=headers, json=test_block)
    print(f"Post Test Block ({res.status_code})")
    
    res = requests.get(f"{SB_URL}/rest/v1/blocks?id=eq.8888", headers=headers)
    print(f"Verify Test Block: {res.text}")

if __name__ == "__main__":
    test()
