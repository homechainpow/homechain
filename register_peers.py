import requests
import json

nodes = [
    "http://ec2-3-84-153-5.compute-1.amazonaws.com:5005",
    "http://ec2-34-229-24-221.compute-1.amazonaws.com:5005"
]

for node in nodes:
    try:
        res = requests.post("http://localhost:5005/register_node", json={"address": node.replace("http://", "")})
        print(f"Registered {node}: {res.status_code}")
    except Exception as e:
        print(f"Failed to register {node}: {e}")

# Check local peers
try:
    res = requests.get("http://localhost:5005/debug/state")
    print(f"\nLocal Node State: {res.json().get('nodes', [])}")
except:
    pass
