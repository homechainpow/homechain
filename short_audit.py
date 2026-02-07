
import requests
d = requests.get("http://localhost:5005/chain").json()
vals = d.get("validators", [])
print(f"COUNT:{len(vals)}")
for v in vals:
    print(f"VAL:{v}")
