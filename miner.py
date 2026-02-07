import requests
import time
import hashlib
import json
import argparse
import multiprocessing
import sys

def hashing_worker(block_prefix, target, start_nonce, step, result_queue):
    """
    Independent worker process for hashing.
    """
    nonce = start_nonce
    while True:
        # Check if another process found it (queue not empty)
        if not result_queue.empty():
            return

        # Fast Hashing
        data_string = f"{block_prefix}{nonce}"
        h = hashlib.sha256(data_string.encode()).hexdigest()
        
        if int(h, 16) < target:
            result_queue.put((nonce, h))
            return
        
        nonce += step
        if nonce % 20000 == 0:
            # We don't print in workers to avoid overlapping output
            pass

def start_miner(node_url, wallet_address, threads=1, throttle=0, device_id='unknown'):
    print(f"⛏️ HomeChain Multi-Miner Started")
    print(f"📡 Node: {node_url}")
    print(f"💰 Wallet: {wallet_address}")
    print(f"🚀 Threads: {threads}")
    
    while True:
        try:
            # 1. Get Work
            response = requests.get(f"{node_url}/mining/get-work?address={wallet_address}&device_id={device_id}")
            if response.status_code != 200:
                print("Waiting for work...")
                time.sleep(2)
                continue
            
            work = response.json()
            target = work['target']
            index = work['index']
            print(f"\n[Block #{index}] Mining with {threads} threads...")
            
            # Prepare fixed block data string once (Merkle Root V2)
            merkle_root = work.get('merkle_root', "0" * 64)
            block_prefix = f"{work['index']}{work['previous_hash']}{work['timestamp']}{merkle_root}{wallet_address}"
            
            result_queue = multiprocessing.Queue()
            processes = []
            
            # Start Worker Processes
            for i in range(threads):
                p = multiprocessing.Process(
                    target=hashing_worker, 
                    args=(block_prefix, target, i, threads, result_queue)
                )
                p.daemon = True
                p.start()
                processes.append(p)
            
            start_t = time.time()
            found_data = None
            
            # Monitor workers or check for Work Refresh
            while True:
                time.sleep(1) # Check state every 1s
                
                # Check if someone found the block
                if not result_queue.empty():
                    found_data = result_queue.get()
                    break
                
                # Check for Work Refresh (30s)
                if time.time() - start_t > 30:
                    print("Refreshing work...")
                    break
            
            # Clean up processes
            for p in processes:
                p.terminate()
            
            if found_data:
                nonce, hash_res = found_data
                end_t = time.time()
                print(f"💎 FOUND BLOCK! Nonce: {nonce} Hash: {hash_res}")
                print(f"Time Taken: {end_t - start_t:.2f}s")
                
                submit_data = work.copy()
                submit_data['nonce'] = nonce
                submit_data['hash'] = hash_res
                submit_data['validator'] = wallet_address
                
                res = requests.post(f"{node_url}/mining/submit", json=submit_data)
                print(f"Submission: {res.text}")

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    multiprocessing.freeze_support() # For Windows compatibility
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--node', default='http://localhost:5005', help='Node URL')
    parser.add_argument('--address', help='Manual Wallet Address')
    parser.add_argument('--wallet-file', help='Path to wallet.pem file')
    parser.add_argument('--threads', type=int, default=1, help='CPU Threads')
    parser.add_argument('--throttle', type=float, default=0, help='Legacy throttle (unused)')
    parser.add_argument('--device-id', default='unknown', help='Unique device ID')
    args = parser.parse_args()
    
    address = args.address
    
    if args.wallet_file:
        try:
            from ecdsa import SigningKey
            import os
            with open(args.wallet_file, "rb") as f:
                pem = f.read()
            sk = SigningKey.from_pem(pem)
            address = sk.verifying_key.to_string().hex()
            print(f"🔓 Loaded Wallet: {address[:16]}...")
        except Exception as e:
            print(f"Error loading wallet: {e}")
            exit(1)
            
    if not address:
        print("Error: Provide --address or --wallet-file")
        exit(1)
    
    start_miner(args.node, address, args.threads, args.throttle, args.device_id)
