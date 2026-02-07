
import requests
import json

def audit():
    seed_ip = "13.220.55.223"
    try:
        r = requests.get(f"http://{seed_ip}:5005/nodes")
        nodes = r.json().get("nodes", [])
        print(f"--- Nodes Audit ---")
        print(f"Total Nodes: {len(nodes) + 1}")
        print(f"Seed: {seed_ip}")
        for n in nodes:
            print(f"Peer: {n}")
            
        r = requests.get(f"http://{seed_ip}:5005/chain")
        data = r.json()
        validators = data.get("validators", [])
        print(f"\n--- Validators Audit ---")
        print(f"Total Unique Validators: {len(validators)}")
        # Check if our new ones are there
        vps1 = "7651ba54ae51a990abdefa0d7d0a4b86521bc7d973cb70a4ae4314b64b18f081"
        vps2 = "8c0829602c7bbbbf6612a284e8f47c87023363364f9f25793e1107563c6b6534"
        if vps1 in validators: print("VPS 1 Validator: REGISTERED")
        if vps2 in validators: print("VPS 2 Validator: REGISTERED")
        
        print(f"\nNetwork Height: {data.get('length')}")
        print(f"Total Supply: {data.get('supply')}")

    except Exception as e:
        print(f"Audit Error: {e}")

if __name__ == "__main__":
    audit()
