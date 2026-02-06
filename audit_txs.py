
import requests
import json

node_url = "http://localhost:5005"
start = 491
end = 510

total_txs = 0
for i in range(start, end):
    try:
        res = requests.get(f"{node_url}/blocks/range?start={i}&end={i+1}", timeout=5)
        blocks = res.json().get('blocks', [])
        for b in blocks:
            tx_count = len(b.get('transactions', []))
            total_txs += tx_count
            if tx_count > 0:
                print(f"BLOCK {b['index']} has {tx_count} transactions.")
    except Exception as e:
        print(f"Error at block {i}: {e}")

print(f"TOTAL TRANSACTIONS FOUND: {total_txs}")
