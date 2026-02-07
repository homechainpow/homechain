
import requests
import json
import time
import hashlib

def test_speed():
    try:
        r = requests.get("http://localhost:5005/mining/get-work?address=speedtest")
        work = r.json()
        txs = work['transactions']
        print(f"TX Count in Block: {len(txs)}")
        tx_str = json.dumps(txs, sort_keys=True)
        print(f"Data String Size: {len(tx_str) / 1024:.2f} KB")
        
        start = time.time()
        count = 1000
        for i in range(count):
            data = f"{work['index']}{work['previous_hash']}{work['timestamp']}{tx_str}{'speedtest'}{i}"
            hashlib.sha256(data.encode()).hexdigest()
            
        elapsed = time.time() - start
        print(f"Speed: {count / elapsed:.2f} H/s")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_speed()
