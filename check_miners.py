import requests
import json

SUPABASE_URL = "https://fzvthnswwubvntfexyyo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ6dnRobnN3d3Vidm50ZmV4eXlvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg3NjQyMDUsImV4cCI6MjA1NDM0MDIwNX0.uFNDQ-mC_G_2g0n0O_6n-y1m8F0O7u6n9J_Y_5u_6Y"

def check_holders():
    url = f"{SUPABASE_URL}/rest/v1/holders?select=*"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        holders = response.json()
        print(f"Found {len(holders)} holders.")
        for h in holders:
            if "M" in str(h.get('address', '')) or "M" in str(h.get('wallet_name', '')):
                print(h)
    else:
        print(f"Error fetching holders: {response.text}")

if __name__ == "__main__":
    check_holders()
