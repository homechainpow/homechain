import requests
import re

# Configuration
with open('supabase_sync.py', 'r') as f:
    content = f.read()
    sb_url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    sb_key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

headers = {
    "apikey": sb_key,
    "Authorization": f"Bearer {sb_key}",
    "Content-Type": "application/json"
}

# Addresses
full_addr = "aa0ba2e22c9cd4a6bc50b5cb993a87ad9ff39e6c249460378799bb93216ed69d44a16d905db4b27c6305b19317420f4f2d6d66ab06e77b1ad5796646b212364c"
trunc_addr = "aa0ba2e22c9cd4a6bc50b5c18bab9685ed69f9876e6b093390c7511d433644d96796646b212364c6e77b1ad57"

def migrate_history():
    print(f"[*] Migrating history from {trunc_addr[:8]}... to {full_addr[:8]}...")
    
    # 1. Update transactions sender
    res = requests.patch(f"{sb_url}/rest/v1/transactions?sender=eq.{trunc_addr}", headers=headers, json={"sender": full_addr})
    print(f"  [+] Transactions (Sender): {res.status_code}")
    
    # 2. Update transactions receiver
    res = requests.patch(f"{sb_url}/rest/v1/transactions?receiver=eq.{trunc_addr}", headers=headers, json={"receiver": full_addr})
    print(f"  [+] Transactions (Receiver): {res.status_code}")
    
    # 3. Update rewards receiver
    res = requests.patch(f"{sb_url}/rest/v1/rewards?receiver=eq.{trunc_addr}", headers=headers, json={"receiver": full_addr})
    print(f"  [+] Rewards (Receiver): {res.status_code}")
    
    # 4. Update blocks validator
    res = requests.patch(f"{sb_url}/rest/v1/blocks?validator=eq.{trunc_addr}", headers=headers, json={"validator": full_addr})
    print(f"  [+] Blocks (Validator): {res.status_code}")

    print("[✓] Migration Finished.")

if __name__ == "__main__":
    migrate_history()
