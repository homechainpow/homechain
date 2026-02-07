
import requests
d = requests.get('http://13.220.55.223:5005/chain').json()
print(f'Validators: {len(d["validators"])}')
v1 = "7651ba54ae51a990abdefa0d7d0a4b86521bc7d973cb70a4ae4314b64b18f081"
v2 = "8c0829602c7bbbbf6612a284e8f47c87023363364f9f25793e1107563c6b6534"
print(f'VPS1 Found: {v1 in d["validators"]}')
print(f'VPS2 Found: {v2 in d["validators"]}')
