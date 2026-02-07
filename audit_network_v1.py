
import requests
import json

def audit():
    try:
        r = requests.get("http://localhost:5005/chain")
        d = r.json()
        validators = d.get("validators", [])
        queue = d.get("reward_queue", [])
        
        print(f"--- Global Network Audit ---")
        print(f"Total Unique Validators: {len(validators)}")
        for v in validators:
            print(f"  - {v}")
            
        print(f"\nReward Queue (Active Miners): {len(queue)}")
        for q in queue:
            print(f"  - {q}")
            
        # Check last 10 blocks for miner diversity
        blocks = d.get("chain", [])[-10:]
        print(f"\nLast 10 Blocks Mining History:")
        for b in blocks:
            print(f"  Block #{b['index']} mined by: {b['validator']}")
            
    except Exception as e:
        print(f"Audit failed: {e}")

if __name__ == "__main__":
    audit()
