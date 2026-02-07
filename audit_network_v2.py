
import requests
import json

def audit():
    try:
        r = requests.get("http://localhost:5005/chain")
        d = r.json()
        validators = d.get("validators", [])
        
        print(f"--- Global Network Audit ---")
        print(f"Nodes Registered: {requests.get('http://localhost:5005/nodes').json().get('nodes', [])}")
        
        print(f"Total Unique Validators (Miners): {len(validators)}")
        for i, v in enumerate(validators):
            print(f"  {i+1}. {v}")
            
        # Check reward queue to see who is currently mining/eligible
        print(f"\nActive Reward Queue: {d.get('reward_queue', [])}")
        
        # Check last 5 blocks to see which miner is winning
        blocks = d.get("chain", [])[-5:]
        print(f"\nLast 5 Blocks Mining Activity:")
        for b in blocks:
            print(f"  Block #{b['index']} mined by: {b['validator']}")
            
    except Exception as e:
        print(f"Audit failed: {e}")

if __name__ == "__main__":
    audit()
