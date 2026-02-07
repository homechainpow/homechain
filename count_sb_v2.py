
import requests
SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"
headers = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Range": "0-0"}

def count_accurate():
    # Use Range header and check Content-Range
    r = requests.get(f"{SB_URL}/rest/v1/transactions?select=id", headers=headers)
    print(f"Transactions: {r.headers.get('Content-Range')}")
    r = requests.get(f"{SB_URL}/rest/v1/rewards?select=id", headers=headers)
    print(f"Rewards: {r.headers.get('Content-Range')}")

if __name__ == "__main__":
    count_accurate()
