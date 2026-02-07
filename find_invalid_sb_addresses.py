import requests
import re

with open('supabase_sync.py', 'r') as f:
    content = f.read()
    url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

# Fetch all holders
res = requests.get(f"{url}/rest/v1/holders", headers=headers)
holders = res.json()

invalid = []
for h in holders:
    addr = h['address']
    # Valid = 128 chars hex
    if len(addr) != 128:
        invalid.append(h)
    else:
        try:
            int(addr, 16)
        except:
            invalid.append(h)

print(f"Total Invalid Addresses found: {len(invalid)}")
for inv in invalid[:10]:
    print(inv)
