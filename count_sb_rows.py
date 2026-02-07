
import requests
SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"
headers = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}

def count():
    r = requests.get(f"{SB_URL}/rest/v1/transactions?select=id", headers=headers, params={"count": "exact"})
    print(f"Transactions Count: {r.headers.get('Content-Range')}")
    r = requests.get(f"{SB_URL}/rest/v1/rewards?select=id", headers=headers, params={"count": "exact"})
    print(f"Rewards Count: {r.headers.get('Content-Range')}")

if __name__ == "__main__":
    count()
