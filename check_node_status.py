
import requests
import json
try:
    node_url = "http://localhost:5005"
    res = requests.get(f"{node_url}/chain", timeout=10)
    data = res.json()
    print(f"HEIGHT:{data['length']}")
    print(f"PENDING:{len(data.get('pending_transactions', []))}")
    
    # Check latest block for transactions
    if data['chain']:
        last_block = data['chain'][-1]
        print(f"LAST_BLOCK_INDEX:{last_block['index']}")
        print(f"LAST_BLOCK_TX_COUNT:{len(last_block.get('transactions', []))}")
except Exception as e:
    print(f"ERROR: {e}")
