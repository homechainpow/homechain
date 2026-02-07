import requests
import json

URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"

headers = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Prefer": "count=exact"
}

def audit():
    tables = ["blocks", "transactions", "rewards", "holders", "stats"]
    print(f"Checking {URL}...")
    for t in tables:
        h = headers.copy()
        h["Prefer"] = "count=exact"
        res = requests.get(f"{URL}/rest/v1/{t}?select=*", headers=h)
        if res.status_code == 200:
            count = len(res.json())
            print(f"{t}: {count}")
        else:
            print(f"{t}: Error {res.status_code}")

if __name__ == "__main__":
    audit()
