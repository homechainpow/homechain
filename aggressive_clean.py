import requests
import json
import time

SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "count=exact"
}

def clean():
    targets = ["transactions", "rewards", "blocks", "holders", "stats"]
    print("--- Aggressive Supabase Clean ---")
    
    for table in targets:
        print(f"[*] Cleaning {table}...")
        # 1. Check Count
        res = requests.get(f"{SB_URL}/rest/v1/{table}?select=*", headers=headers)
        if res.status_code == 200:
            count = len(res.json())
            print(f"    Current Rows: {count}")
            if count > 0:
                # 2. Delete All (id > -1 or using not.is.null)
                # For holders and stats we might need address or id
                filter_col = "id"
                if table == "holders": filter_col = "address"
                
                del_res = requests.delete(f"{SB_URL}/rest/v1/{table}?{filter_col}=not.is.null", headers=headers)
                print(f"    Delete Resp: {del_res.status_code}")
                
                # Verify
                ver_res = requests.get(f"{SB_URL}/rest/v1/{table}?select=*", headers=headers)
                new_count = len(ver_res.json())
                print(f"    New Rows: {new_count}")
        else:
            print(f"    Error checking {table}: {res.status_code}")

    print("[*] Re-initializing stats...")
    payload = {"id": 1, "height": 0, "total_supply": 0, "total_txs": 0}
    requests.post(f"{SB_URL}/rest/v1/stats", headers=headers, json=payload)
    print("    Stats reset.")

if __name__ == "__main__":
    clean()
