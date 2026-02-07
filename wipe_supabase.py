
import requests

SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

def wipe():
    # Define tables and their filter columns
    targets = {
        "transactions": "block_id", # block_id is always present
        "rewards": "block_id",
        "blocks": "id",
        "holders": "address"
    }
    
    for table, col in targets.items():
        print(f"[*] Wiping table: {table}")
        # Use a filter that matches all rows (not null)
        res = requests.delete(f"{SB_URL}/rest/v1/{table}?{col}=not.is.null", headers=headers)
        print(f"  Response: {res.status_code}")
    
    print("[*] Resetting stats height...")
    res = requests.patch(f"{SB_URL}/rest/v1/stats?id=eq.1", headers=headers, json={"height": 0, "total_supply": 0})
    print(f"  Response: {res.status_code}")

if __name__ == "__main__":
    wipe()
