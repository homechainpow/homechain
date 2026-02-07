
import requests
import time

def check_activity():
    try:
        # Check last block
        chain = requests.get("http://localhost:5005/chain").json()['chain']
        last_block = chain[-1]
        print(f"Latest Block: #{last_block['index']}")
        txs = last_block.get('transactions', [])
        print(f"TXs in user block: {len(txs)}")
        
        stress_txs = [t for t in txs if isinstance(t.get('data'), dict) and t['data'].get('type') == 'stress_test']
        print(f"Stress Test TXs in block: {len(stress_txs)}")
        if stress_txs:
            print(f"Sample Data: {stress_txs[0]['data']}")
            
        # Check Mempool
        mp = requests.get("http://localhost:5005/mempool").json()
        print(f"Mempool Count: {mp['count']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_activity()
