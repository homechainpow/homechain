import os
import time
import random
import requests
from ecdsa import SigningKey
from wallet import Transaction

# Configuration
NODE_URL = "http://localhost:5005"
WALLETS_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\HomeChain\wallets_300"
TOTAL_TRANSACTIONS = 9000
TPS = 3  # Transactions per second
DELAY = 1.0 / TPS  # ~0.333 seconds between transactions
MIN_AMOUNT = 100 * 10**8  # 100 HOME in satoshis
MAX_AMOUNT = 500 * 10**8  # 500 HOME in satoshis
MIN_FEE = 1_000_000  # 0.01 HOME

def load_wallets():
    """Load all wallet PEM files from the directory."""
    wallets = []
    for filename in os.listdir(WALLETS_DIR):
        if filename.endswith('.pem'):
            filepath = os.path.join(WALLETS_DIR, filename)
            try:
                with open(filepath, 'rb') as f:
                    sk = SigningKey.from_pem(f.read())
                    address = sk.verifying_key.to_string().hex()
                    wallets.append((address, sk, filename))
            except Exception as e:
                print(f"[!] Failed to load {filename}: {e}")
    return wallets

def send_transaction(sender_addr, sender_sk, receiver_addr, amount, fee=MIN_FEE):
    """Send a transaction to the node."""
    tx = Transaction(sender_addr, receiver_addr, amount, fee)
    tx.sign(sender_sk)
    
    try:
        res = requests.post(f"{NODE_URL}/transactions/new", json=tx.to_dict(), timeout=5)
        if res.status_code == 201:
            return True, "Success"
        else:
            return False, res.text
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("HomeChain V2 Stress Test - 300 Wallets Edition")
    print("=" * 60)
    print(f"Target: {TOTAL_TRANSACTIONS:,} transactions")
    print(f"Rate: {TPS} TPS (~{DELAY:.3f}s delay)")
    print(f"Amount Range: {MIN_AMOUNT // 10**8} - {MAX_AMOUNT // 10**8} HOME")
    print("=" * 60)
    
    # Load wallets
    print("\n[*] Loading wallets...")
    wallets = load_wallets()
    if len(wallets) < 2:
        print("[!] Error: Need at least 2 wallets to run stress test.")
        return
    
    print(f"[✓] Loaded {len(wallets)} wallets")
    
    # Run stress test
    print(f"\n[*] Starting stress test loop...\n")
    
    success_count = 0
    fail_count = 0
    start_time = time.time()
    
    for i in range(TOTAL_TRANSACTIONS):
        # Pick random sender and receiver
        sender_addr, sender_sk, sender_name = random.choice(wallets)
        receiver_addr, _, receiver_name = random.choice(wallets)
        
        # Ensure sender != receiver
        while receiver_addr == sender_addr:
            receiver_addr, _, receiver_name = random.choice(wallets)
        
        # Random amount
        amount = random.randint(MIN_AMOUNT, MAX_AMOUNT)
        
        # Send transaction
        success, msg = send_transaction(sender_addr, sender_sk, receiver_addr, amount)
        
        if success:
            success_count += 1
            status = "✓"
        else:
            fail_count += 1
            status = "✗"
        
        # Progress report every 100 transactions
        if (i + 1) % 100 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            print(f"[{status}] TX {i+1:,}/{TOTAL_TRANSACTIONS:,} | Success: {success_count} | Fail: {fail_count} | Rate: {rate:.2f} TPS")
        
        # Rate limiting
        time.sleep(DELAY)
    
    # Final report
    elapsed = time.time() - start_time
    avg_tps = TOTAL_TRANSACTIONS / elapsed if elapsed > 0 else 0
    
    print("\n" + "=" * 60)
    print("STRESS TEST COMPLETE")
    print("=" * 60)
    print(f"Total Transactions: {TOTAL_TRANSACTIONS:,}")
    print(f"Successful: {success_count:,}")
    print(f"Failed: {fail_count:,}")
    print(f"Duration: {elapsed:.2f}s")
    print(f"Average TPS: {avg_tps:.2f}")
    print("=" * 60)

if __name__ == "__main__":
    main()
