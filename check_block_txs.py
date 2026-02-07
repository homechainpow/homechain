
import requests
import sys

def check(idx):
    r = requests.get(f"http://localhost:5005/block/{idx}")
    if r.status_code == 200:
        b = r.json()
        txs = b.get("transactions", [])
        print(f"Block #{idx} has {len(txs)} transactions.")
        if txs:
            print(f"First TX ID: {txs[0].get('signature', 'N/A')[:10]}...")
    else:
        print(f"Block #{idx} not found.")

if __name__ == "__main__":
    idx = 584
    if len(sys.argv) > 1:
        idx = int(sys.argv[1])
    check(idx)
