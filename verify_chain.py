import requests
import time
import json
import sys
from wallet import Wallet, Transaction

BASE_URL = "http://localhost:5000"
LOG_FILE = "verify_output.txt"

def log(msg):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def test_chain():
    log("Fetching Blockchain...")
    res = requests.get(f"{BASE_URL}/chain")
    log(str(res.json()))
    return len(res.json()['chain'])

def test_tx():
    log("Submitting Signed Transaction...")
    # Generate a wallet
    sender_wallet = Wallet()
    receiver_wallet = Wallet()
    
    # Create TX locally
    tx = Transaction(sender_wallet.address, receiver_wallet.address, 10, {"message": "Hello Signed World"})
    # Sign it
    sender_wallet.sign_transaction(tx)
    
    # Send to Node
    res = requests.post(f"{BASE_URL}/transactions/new", json=tx.to_dict())
    log(f"Tx Response: {res.json()}")

def test_mine():
    log("Mining Block...")
    res = requests.get(f"{BASE_URL}/mine")
    log(str(res.json()))

def test_name_service():
    log("Registering Name 'satya.home'...")
    sender_wallet = Wallet()
    
    # 1. Create & Sign Register TX
    tx = Transaction(
        sender=sender_wallet.address, 
        receiver="0x0000", 
        amount=0, 
        data={
            "contract": "0x02",
            "action": "register",
            "name": "satya.home"
        }
    )
    sender_wallet.sign_transaction(tx)
    
    # Submit
    res = requests.post(f"{BASE_URL}/transactions/new", json=tx.to_dict())
    log(f"Register Tx Response: {res.json()}")
    
    # 2. Mine
    time.sleep(1)
    res = requests.get(f"{BASE_URL}/mine")
    log(f"Mine Response: {res.json()}")
    
    # 3. Resolve
    log("Resolving 'satya.home'...")
    res = requests.get(f"{BASE_URL}/resolve/satya.home")
    log(f"Resolve Response: {res.json()}")
    
    if res.status_code == 200 and res.json().get('address') == sender_wallet.address:
        log("SUCCESS: Name resolved correctly.")
    else:
        log("FAILURE: Name resolution failed.")

try:
    # Clear log
    with open(LOG_FILE, "w") as f: f.write("")
    
    log("Wait for Node...")
    time.sleep(2)
    
    initial_height = test_chain()
    test_tx()
    test_mine()
    new_height = test_chain()
    
    if new_height == initial_height + 1:
        log("SUCCESS: Block height increased.")
    else:
        log("FAILURE: Block height did not increase.")

    test_name_service()
    
except Exception as e:
    log(f"ERROR: {e}")
