
import requests
d = requests.get("http://localhost:5005/chain").json()
chain = d.get("chain", [])
print(f"CHAIN_LEN:{len(chain)}")
for b in chain[:20]:
    print(f"BLOCK:{b['index']} VAL:{b['validator'][:10]}")
