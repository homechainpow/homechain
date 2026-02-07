
import requests
import time

def check_throughput():
    try:
        # Check Mempool
        mp = requests.get("http://localhost:5005/mempool").json()
        print(f"Mempool Count: {mp.get('count', 'Unknown')}")

        # Check Chain
        chain = requests.get("http://localhost:5005/chain").json()['chain'][-10:]
        
        print("\nRecent Blocks:")
        last_ts = 0
        for b in chain:
            ts = b['timestamp']
            diff = ts - last_ts if last_ts > 0 else 0
            tx_count = len(b.get('transactions', []))
            print(f"Block #{b['index']} | TXs: {tx_count} | Interval: {diff:.2f}s")
            last_ts = ts
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_throughput()
