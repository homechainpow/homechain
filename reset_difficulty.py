import json
import os

MAX_TARGET = 0x0000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

chain_file = '/home/ubuntu/HomeChain/chain_data.json'

if os.path.exists(chain_file):
    with open(chain_file, 'r') as f:
        chain = json.load(f)
    
    if chain:
        old_target = chain[-1].get('target', 0)
        print(f'[*] Old Target: {hex(old_target)}')
        chain[-1]['target'] = MAX_TARGET
        print(f'[*] New Target: {hex(MAX_TARGET)}')
        
        with open(chain_file, 'w') as f:
            json.dump(chain, f, indent=4)
        print('[+] Difficulty Reset Successfully!')
else:
    print(f'[!] {chain_file} not found!')
