import requests
import json
import re

# Configuration
with open('supabase_sync.py', 'r') as f:
    content = f.read()
    sb_url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    sb_key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

headers = {
    "apikey": sb_key,
    "Authorization": f"Bearer {sb_key}"
}

def verify_results():
    print(f"[*] Verifying holders on {sb_url}...")
    url = f"{sb_url}/rest/v1/holders?select=address,balance&order=balance.desc&limit=10"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        print("\n--- Top 10 Holders in Supabase ---")
        for i, holder in enumerate(data):
            print(f"{i+1}. {holder['address'][:16]}... | Balance: {holder['balance']/10**8:,.2f} HOME")
        
        # Check for labels
        print("\n--- Label Check ---")
        labels = ["S_901", "SYSTEM", "GENESIS", "M1"]
        for label in labels:
            url = f"{sb_url}/rest/v1/holders?address=eq.{label}"
            res = requests.get(url, headers=headers)
            if len(res.json()) == 0:
                print(f"  [✓] Label {label} is GONE.")
            else:
                print(f"  [✗] Label {label} is STILL PRESENT!")
    else:
        print(f"  [!] Error: {res.status_code} - {res.text}")

if __name__ == "__main__":
    verify_results()
