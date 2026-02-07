
import requests
import time
from datetime import datetime

def audit_timing():
    url = "http://localhost:5005/chain"
    try:
        r = requests.get(url)
        data = r.json()
        chain = data.get("chain", [])
        if not chain:
            print("Chain empty")
            return
            
        print(f"--- Block Timing Audit ---")
        print(f"Current Time: {datetime.now().strftime('%H:%M:%S')}")
        
        last_5 = chain[-5:]
        for b in reversed(last_5):
            ts = b.get("timestamp")
            dt = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            tx_count = len(b.get("transactions", []))
            print(f"Block #{b['index']} | Time: {dt} | Txs: {tx_count} | Hash: {b['hash'][:10]}...")
            
        if len(chain) >= 1:
            last_ts = chain[-1]['timestamp']
            diff = time.time() - last_ts
            print(f"\nTime since last block: {int(diff // 60)}m {int(diff % 60)}s")
            
        print(f"Mempool Count: {requests.get('http://localhost:5005/mempool').json().get('count')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_timing()
