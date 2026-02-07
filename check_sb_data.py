
import requests
SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

def check_txs():
    url = f"{SB_URL}/rest/v1/transactions?select=*&order=timestamp.desc&limit=5"
    r = requests.get(url, headers=headers)
    print(f"Transactions (Latest):")
    print(r.json())
    
    url = f"{SB_URL}/rest/v1/rewards?select=*&order=timestamp.desc&limit=5"
    r = requests.get(url, headers=headers)
    print(f"\nRewards (Latest):")
    print(r.json())

if __name__ == "__main__":
    check_txs()
