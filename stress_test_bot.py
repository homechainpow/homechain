#!/usr/bin/env python3
"""
HomeChain V2 Stress Test Bot
Generates random transactions to test network throughput and scanner display.
"""

import requests
import time
import random
from ecdsa import SigningKey, SECP256k1
import hashlib
import json
import os

WALLETS_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\HomeChain\wallets"

class StressTestBot:
    def __init__(self, wallets_dir=WALLETS_DIR):
        print(f"🤖 Initializing Stress Test Bot using wallets from: {wallets_dir}")
        self.wallets = []
        self.node_url = NODE_URL
        
        # Scan for PEM files
        if not os.path.exists(wallets_dir):
            print(f"❌ Error: Wallets directory not found at {wallets_dir}")
            return

        pem_files = [f for f in os.listdir(wallets_dir) if f.endswith('.pem')]
        # Filter p1-p100
        p_wallets = [f for f in pem_files if f.startswith('p') and f[1:-4].isdigit()]
        p_wallets.sort(key=lambda x: int(x[1:-4])) # Sort p1, p2... p100

        print(f"  📂 Found {len(p_wallets)} test wallets (p1.pem - p{len(p_wallets)}.pem)")
        
        for i, filename in enumerate(p_wallets):
            pem_path = os.path.join(wallets_dir, filename)
            try:
                with open(pem_path, 'r') as f:
                    sk = SigningKey.from_pem(f.read())
                    address = sk.verifying_key.to_string().hex()
                    self.wallets.append({
                        'id': i + 1,
                        'name': filename,
                        'sk': sk,
                        'address': address,
                        'balance': 0
                    })
            except Exception as e:
                print(f"  ❌ Error loading {filename}: {e}")
        
        print(f"\n🚀 Bot Ready! {len(self.wallets)} wallets available.\n")
    
    def get_balance(self, address):
        """Get balance from node"""
        try:
            resp = requests.get(f"{self.node_url}/balance/{address}", timeout=5)
            if resp.status_code == 200:
                return resp.json().get('balance', 0)
        except:
            pass
        return 0
    
    def sign_transaction(self, sender_sk, sender_addr, receiver_addr, amount, fee=1_000_000):
        """Create and sign a transaction"""
        tx = {
            "sender": sender_addr,
            "receiver": receiver_addr,
            "amount": amount,
            "fee": fee,
            "data": {"type": "stress_test"},
            "timestamp": time.time(),
            "signature": None
        }
        
        # Compute hash (without signature)
        tx_copy = tx.copy()
        del tx_copy["signature"]
        tx_string = json.dumps(tx_copy, sort_keys=True)
        tx_hash = hashlib.sha256(tx_string.encode()).hexdigest()
        
        # Sign
        signature = sender_sk.sign(tx_hash.encode()).hex()
        tx["signature"] = signature
        
        return tx
    
    def submit_transaction(self, tx):
        """Submit transaction to node"""
        try:
            resp = requests.post(f"{self.node_url}/transaction", json=tx, timeout=5)
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.text
        except Exception as e:
            return False, str(e)
    
    def run_stress_test(self, duration_seconds=300, tx_per_second=2):
        """Run stress test for specified duration"""
        print(f"⚡ Starting Stress Test")
        print(f"   Duration: {duration_seconds}s")
        print(f"   Target TPS: {tx_per_second}")
        print(f"   Total TXs: ~{duration_seconds * tx_per_second}\n")
        
        start_time = time.time()
        tx_count = 0
        success_count = 0
        
        while time.time() - start_time < duration_seconds:
            # Random sender and receiver
            sender = random.choice(self.wallets)
            receiver = random.choice([w for w in self.wallets if w['id'] != sender['id']])
            
            # Check balance
            balance = self.get_balance(sender['address'])
            
            # Random amount (1-100 $HOME)
            amount = random.randint(1 * 10**8, 100 * 10**8)
            fee = 1_000_000
            
            if balance >= (amount + fee):
                # Create and submit transaction
                tx = self.sign_transaction(
                    sender['sk'],
                    sender['address'],
                    receiver['address'],
                    amount,
                    fee
                )
                
                success, result = self.submit_transaction(tx)
                tx_count += 1
                
                if success:
                    success_count += 1
                    print(f"✅ TX #{tx_count}: {sender['id']} → {receiver['id']} | {amount / 10**8:.2f} $HOME | Balance: {balance / 10**8:.2f}")
                else:
                    print(f"❌ TX #{tx_count}: Failed - {result}")
            else:
                print(f"⏭️  Skipping {sender['id']} (insufficient balance: {balance / 10**8:.2f} $HOME)")
            
            # Rate limiting
            time.sleep(1 / tx_per_second)
        
        elapsed = time.time() - start_time
        print(f"\n📊 Stress Test Complete!")
        print(f"   Duration: {elapsed:.1f}s")
        print(f"   Total TXs: {tx_count}")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {tx_count - success_count}")
        print(f"   Success Rate: {(success_count / tx_count * 100) if tx_count > 0 else 0:.1f}%")
        print(f"   Actual TPS: {tx_count / elapsed:.2f}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='HomeChain V2 Stress Test Bot')
    parser.add_argument('--node', default='http://localhost:5005', help='Node URL')
    parser.add_argument('--wallets-dir', default=WALLETS_DIR, help='Directory containing .pem wallets')
    parser.add_argument('--duration', type=int, default=300, help='Test duration in seconds')
    parser.add_argument('--tps', type=float, default=2, help='Target transactions per second')
    args = parser.parse_args()
    
    NODE_URL = args.node
    WALLETS_DIR = args.wallets_dir
    
    bot = StressTestBot(wallets_dir=WALLETS_DIR)
    if bot.wallets:
        bot.run_stress_test(duration_seconds=args.duration, tx_per_second=args.tps)
    else:
        print("❌ No wallets found. Exiting.")
