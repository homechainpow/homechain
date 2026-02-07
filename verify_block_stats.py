import requests
import json
import sys

# Seed Node URL
NODE_URL = 'http://localhost:5005'

def get_stats():
    try:
        # Get Chain
        r = requests.get(f'{NODE_URL}/chain')
        if r.status_code != 200:
            print(f'ERROR: Node returned {r.status_code}')
            return
            
        data = r.json()
        chain = data.get('chain', [])
        
        if not chain:
            print('STATUS: CHAIN_EMPTY')
            return
            
        last_block = chain[-1]
        height = last_block['index']
        tx_count = len(last_block.get('transactions', []))
        
        print(f'LATEST_BLOCK_INDEX: {height}')
        print(f'LATEST_BLOCK_TX_COUNT: {tx_count}')
        print(f'CHAIN_TOTAL_BLOCKS: {len(chain)}')
        
        # Check if Block #612 exists and its tx count if not latest
        if height >= 612:
            b612 = next((b for b in chain if b['index'] == 612), None)
            if b612:
                print(f'BLOCK_612_TX_COUNT: {len(b612.get(\"transactions\", []))}')
            else:
                print('BLOCK_612: NOT_FOUND_IN_LOCALLY_FETCHED_CHAIN')
        
    except Exception as e:
        print(f'ERROR: {str(e)}')

if __name__ == '__main__':
    get_stats()
