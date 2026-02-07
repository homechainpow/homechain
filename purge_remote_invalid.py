import requests
import re

with open('supabase_sync.py', 'r') as f:
    content = f.read()
    url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

# 1. Fetch all holders
res = requests.get(f"{url}/rest/v1/holders", headers=headers)
holders = res.json()

invalid_addresses = []
for h in holders:
    addr = h['address']
    if len(addr) != 128 or not all(c in '0123456789abcdef' for c in addr.lower()):
        invalid_addresses.append(addr)

print(f"[*] Found {len(invalid_addresses)} invalid addresses in Supabase.")

# 2. Delete them
deleted_count = 0
for addr in invalid_addresses:
    delete_url = f"{url}/rest/v1/holders?address=eq.{addr}"
    d_res = requests.delete(delete_url, headers=headers)
    if d_res.status_code in [200, 204]:
        deleted_count += 1
    else:
        print(f"  [!] Failed to delete {addr[:16]}... : {d_res.status_code}")

print(f"[✓] Deleted {deleted_count} invalid addresses from Supabase.")
