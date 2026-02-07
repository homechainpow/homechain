import requests
import re
with open('supabase_sync.py', 'r') as f:
    content = f.read()
    url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    key = re.search(r'SB_KEY = "(.*?)"', content).group(1)
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}
h_res = requests.get(f'{url}/rest/v1/holders?select=count', headers={**headers, "Range": "0-0"})
b_res = requests.get(f'{url}/rest/v1/blocks?select=count', headers={**headers, "Range": "0-0"})
print(f"Holders: {h_res.json()}")
print(f"Blocks: {b_res.json()}")
