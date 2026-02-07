import requests
import json

URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"

headers = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json"
}

def audit():
    tables = ["blocks", "transactions", "rewards", "holders", "stats"]
    print(f"--- Supabase Audit for {URL} ---")
    for t in tables:
        h = headers.copy()
        h["Prefer"] = "count=exact"
        res = requests.get(f"{URL}/rest/v1/{t}?select=*", headers=h)
        if res.status_code == 200:
            data = res.json()
            count = len(data)
            print(f"Table {t.ljust(15)}: {count} rows")
            if count > 0:
                print(f"  Sample: {data[:5]}")
        else:
            print(f"Table {t.ljust(15)}: ERROR (Code: {res.status_code}) - {res.text}")

if __name__ == "__main__":
    audit()
