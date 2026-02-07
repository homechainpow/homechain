import requests
import json

SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}"
}

def list_columns():
    url = f"{SB_URL}/rest/v1/holders?limit=1"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        if data:
            print(f"Columns: {list(data[0].keys())}")
        else:
            print("Table is empty.")
    else:
        print(f"Error: {res.text}")

if __name__ == "__main__":
    list_columns()
