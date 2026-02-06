import requests
import time
import hashlib
import json
import argparse
from multiprocessing import Pool, cpu_count

def calculate_hash(index, previous_hash, timestamp, transactions, validator, nonce):
    data_string = f"{index}{previous_hash}{timestamp}{transactions}{validator}{nonce}"
    return hashlib.sha256(data_string.encode()).hexdigest()

def mine_loop(args):
    """
    Mining worker logic.
    """
    target, start_nonce, end_nonce, block_data = args
    index = block_data['index']
    prev_hash = block_data['previous_hash']
    ts = block_data['timestamp']
    txs = json.dumps(block_data['transactions'], sort_keys=True)
    validator = block_data['validator']
    
    nonce = start_nonce
    # Simplified loop
    while nonce < end_nonce:
        data_string = f"{index}{prev_hash}{ts}{txs}{validator}{nonce}"
        res = hashlib.sha256(data_string.encode()).hexdigest()
        if res.startswith(target):
            return nonce, res
        nonce += 1
    return None

def start_miner(node_url, wallet_address, threads=1, throttle=0):
    print(f"⛏️ HomeChain Miner Started")
    print(f"📡 Node: {node_url}")
    print(f"💰 Wallet: {wallet_address}")
    print(f"🚀 Threads: {threads}")
    if throttle > 0:
        print(f"⏳ Throttling: {throttle}s delay every 10,000 hashes")
    
    while True:
        try:
            # 1. Get Work
            response = requests.get(f"{node_url}/mining/get-work?address={wallet_address}&device_id={args.device_id}")
            if response.status_code != 200:
                print("Waiting for work (Node sync/error)...")
                time.sleep(2)
                continue
            
            work = response.json()
            target = work['target']
            
            print(f"\n[Block #{work['index']}] Mining with Target {hex(target)}...")
            
            start_t = time.time()
            nonce = 0
            found = False
            hash_res = ""
            
            while True:
                if time.time() - start_t > 30: # Refresh work every 30s
                    print("Refreshing work...")
                    break 

                # Hashing
                valid_txs_sorted = work['transactions']
                tx_str = json.dumps(valid_txs_sorted, sort_keys=True)
                
                data_string = f"{work['index']}{work['previous_hash']}{work['timestamp']}{tx_str}{wallet_address}{nonce}"
                h = hashlib.sha256(data_string.encode()).hexdigest()
                
                if int(h, 16) < target:
                    found = True
                    hash_res = h
                    break
                
                nonce += 1
                if nonce % 10000 == 0:
                    print(f"Hashes: {nonce}...", end='\r')
                    if throttle > 0:
                        time.sleep(throttle)

            if found:
                end_t = time.time()
                print(f"\n💎 FOUND BLOCK! Nonce: {nonce} Hash: {hash_res}")
                print(f"Speed: {nonce / (end_t - start_t):.2f} H/s")
                
                submit_data = work.copy()
                submit_data['nonce'] = nonce
                submit_data['validator'] = wallet_address
                
                res = requests.post(f"{node_url}/mining/submit", json=submit_data)
                print(f"Submission: {res.text}")
                
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--node', default='http://localhost:5005', help='Node URL')
    parser.add_argument('--address', help='Manual Wallet Address')
    parser.add_argument('--wallet-file', help='Path to wallet.pem file')
    parser.add_argument('--threads', type=int, default=1, help='CPU Threads')
    parser.add_argument('--throttle', type=float, default=0, help='Seconds to sleep every 10k hashes')
    parser.add_argument('--device-id', default='unknown', help='Unique device ID for Anti-Sybil')
    args = parser.parse_args()
    
    address = args.address
    
    if args.wallet_file:
        try:
            from ecdsa import SigningKey
            import os
            if not os.path.exists(args.wallet_file):
                # Fallback for dynamic generation or error
                print(f"Wallet file {args.wallet_file} not found.")
                exit(1)
            with open(args.wallet_file, "rb") as f:
                pem = f.read()
            sk = SigningKey.from_pem(pem)
            address = sk.verifying_key.to_string().hex()
            print(f"🔓 Loaded Wallet from {args.wallet_file}")
        except Exception as e:
            print(f"Error loading wallet file: {e}")
            exit(1)
            
    if not address:
        print("Error: Must provide --address OR --wallet-file")
        exit(1)
    
    start_miner(args.node, address, args.threads, args.throttle)
