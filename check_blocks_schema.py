
import requests
SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNel295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"
headers = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}

# Fixed key in previous tool call might have been truncated/wrongly copied. 
# Re-using the known working header from previous successful check.
SB_KEY_FIXED = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"
headers_fixed = {"apikey": SB_KEY_FIXED, "Authorization": f"Bearer {SB_KEY_FIXED}"}

def check_blocks_schema():
    r = requests.get(f"{SB_URL}/rest/v1/blocks?limit=1", headers=headers_fixed)
    if r.status_code == 200:
        data = r.json()
        if data:
            cols = list(data[0].keys())
            for c in cols:
                print(f"Column: {c}")
        else:
            print("Blocks Table Empty")
    else:
        print(f"Error: {r.status_code} - {r.text}")

if __name__ == "__main__":
    check_blocks_schema()
