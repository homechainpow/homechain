import requests
import json

URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"
ADDR = "7ecac081dec6a78229b0577d3493b8e7343e590059f1ca55b51c9a28a86ffb533ccc"

headers = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}"
}

def check():
    res = requests.get(f"{URL}/rest/v1/holders?address=eq.{ADDR}", headers=headers)
    print(f"Miner Balance in Supabase: {res.text}")
    
    res_stats = requests.get(f"{URL}/rest/v1/stats?id=eq.1", headers=headers)
    print(f"Stats in Supabase: {res_stats.text}")

if __name__ == "__main__":
    check()
