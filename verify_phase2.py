import requests
import time
import sys
from wallet import Wallet, Transaction

BASE_URL = "http://localhost:5000"
LOG_FILE = "verify_phase2_output.txt"

def log(msg):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def check_supply_and_rewards():
    log("\n[TEST] 1. Checking Supply & Rewards Logic")
    res = requests.get(f"{BASE_URL}/chain").json()
    initial_supply = res['supply']
    log(f"Initial Supply: {initial_supply}")
    
    # Mine 1 block (should add 10 HOME)
    requests.get(f"{BASE_URL}/mine")
    
    res = requests.get(f"{BASE_URL}/chain").json()
    new_supply = res['supply']
    log(f"New Supply: {new_supply}")
    
    if new_supply == initial_supply + 10:
        log("SUCCESS: Block Reward correctly minted 10 HOME.")
    else:
        log(f"FAILURE: Supply mismatch. Expected {initial_supply + 10}, got {new_supply}")

def check_persistence_part1():
    log("\n[TEST] 2. Checking Persistence (Write)")
    # We just mined a block. Let's record the height.
    res = requests.get(f"{BASE_URL}/chain").json()
    log(f"Current Height before restart: {res['length']}")
    # The actual restart test must be done by restarting the node process, 
    # which we can't easily automate fully in this script without an external runner.
    # But we can verify the file exists.
    import os
    if os.path.exists("chain_data.json"):
        log("SUCCESS: chain_data.json exists.")
    else:
        log("FAILURE: chain_data.json not found.")

def check_explorer_api():
    log("\n[TEST] 3. Checking Advanced API")
    res = requests.get(f"{BASE_URL}/chain").json()
    validator = res['chain'][-1]['validator']
    
    if validator == "SYSTEM": return
    
    log(f"Checking details for validator: {validator}")
    res = requests.get(f"{BASE_URL}/address/{validator}").json()
    log(f"Balance: {res['balance']}")
    log(f"History Count: {len(res['history'])}")
    
    if 'balance' in res and 'history' in res:
         log("SUCCESS: Address details API works.")
    else:
         log("FAILURE: Address details API invalid.")

try:
    with open(LOG_FILE, "w") as f: f.write("")
    log("Waiting for node...")
    time.sleep(2)
    
    check_supply_and_rewards()
    check_persistence_part1()
    check_explorer_api()
    
except Exception as e:
    log(f"ERROR: {e}")
