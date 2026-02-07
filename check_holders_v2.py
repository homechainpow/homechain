import requests
import json

SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

def check_db():
    headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}"
    }
    
    # 1. Check if M2 or M3 exist as names or addresses
    url = f"{SB_URL}/rest/v1/holders?or=(address.eq.M2,address.eq.M3,wallet_name.eq.M2,wallet_name.eq.M3)"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        print(f"Direct Match for M2/M3: {data}")
    
    # 2. Get top 5 holders by balance
    url = f"{SB_URL}/rest/v1/holders?select=*&order=balance.desc&limit=10"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        print("\nTop 10 Holders:")
        for h in res.json():
            print(f"Address: {h['address']} | Name: {h.get('wallet_name')} | Balance: {h['balance']}")

if __name__ == "__main__":
    check_db()
