import requests
import json

# Using the sync worker's credentials
SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

def find_miners():
    url = f"{SB_URL}/rest/v1/rewards?select=receiver&order=id.desc&limit=1000"
    headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        rewards = response.json()
        receivers = set()
        for r in rewards:
            receivers.add(r['receiver'])
        
        print(f"Found {len(receivers)} unique reward receivers.")
        for addr in sorted(list(receivers)):
            print(addr)
    else:
        print(f"Error fetching rewards: {response.text}")

if __name__ == "__main__":
    find_miners()
