import requests
import re

# Supabase Config
with open('C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/supabase_sync.py', 'r') as f:
    content = f.read()
    sb_url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    sb_key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

headers = {
    "apikey": sb_key,
    "Authorization": f"Bearer {sb_key}"
}

def verify():
    # Check count of holders
    res = requests.get(f"{sb_url}/rest/v1/holders?select=count", headers={**headers, "Range": "0-0"})
    if res.status_code == 200:
        print(f"Total Holders in Supabase: {res.json()}")
    else:
        print(f"Error fetching count: {res.status_code} - {res.text}")

    # Check a few verified addresses
    res_data = requests.get(f"{sb_url}/rest/v1/holders?limit=5", headers=headers)
    if res_data.status_code == 200:
        print("Sample Holders:")
        for h in res_data.json():
            print(f"  {h['address'][:16]}... Balance: {h['balance']}")
    else:
        print(f"Error fetching data: {res_data.status_code}")

if __name__ == "__main__":
    verify()
