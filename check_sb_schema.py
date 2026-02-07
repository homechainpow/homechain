
import requests
SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"
headers = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}

def check_schema():
    # Try to fetch one row with all columns
    r = requests.get(f"{SB_URL}/rest/v1/transactions?limit=1", headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data:
            print("Transactions Columns:", list(data[0].keys()))
        else:
            print("Transactions Table Empty")
    else:
        print(f"Error: {r.status_code} - {r.text}")

if __name__ == "__main__":
    check_schema()
