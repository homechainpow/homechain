import requests
import json

resp = requests.get('http://localhost:5005/mining/get-work?address=test')
data = resp.json()
print(f'Target Int: {data["target"]}')
print(f'Target Hex: {hex(data["target"])}')
print(f'Index: {data["index"]}')
print(f'Transactions: {len(data.get("transactions", []))}')
