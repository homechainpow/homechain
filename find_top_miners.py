import requests
import json
from collections import Counter

SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

def find_top_miners():
    # Fetch recent community rewards (where M2/M3 usually reside)
    url = f"{SB_URL}/rest/v1/rewards?select=receiver,type&limit=2000"
    headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        rewards = response.json()
        community_receivers = [r['receiver'] for r in rewards if r['type'] == 'reward_community']
        counts = Counter(community_receivers).most_common(10)
        
        print(f"Top 10 Community Miners:")
        for addr, count in counts:
            print(f"Address: {addr} | Rewards: {count}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    find_top_miners()
