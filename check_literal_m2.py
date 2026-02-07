import requests
import json

SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}"
}

def check_literal():
    url = f"{SB_URL}/rest/v1/holders?address=eq.M2"
    res = requests.get(url, headers=headers)
    print(f"M2 Check: {res.status_code} - {res.json()}")
    
    url = f"{SB_URL}/rest/v1/holders?address=eq.M3"
    res = requests.get(url, headers=headers)
    print(f"M3 Check: {res.status_code} - {res.json()}")

if __name__ == "__main__":
    check_literal()
