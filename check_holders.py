import requests
import json

# Using creds from supabase_sync.py
SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

def check_holders():
    print("📊 Top 20 Holders in Supabase:")
    url = f"{SB_URL}/rest/v1/holders?select=*&order=balance.desc&limit=20"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        for i, h in enumerate(data):
            print(f"  #{i+1} {h['address']} | Balance: {h['balance']}")
    else:
        print(f"Error: {res.status_code} - {res.text}")

if __name__ == "__main__":
    check_holders()
