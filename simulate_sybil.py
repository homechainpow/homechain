from blockchain import Blockchain, Block
from wallet import Transaction, Wallet
import json
import time

def run_test():
    print("--- STARTING ANTI-SYBIL & ADMIN BYPASS SIMULATION ---")
    bc = Blockchain()
    
    # 1. Normal User Registration
    user1_addr = "0xUSER_A"
    dev1_id = "ANDROID_HP_1"
    
    print(f"\n[Test 1] Normal Registration:")
    bc.register_validator(user1_addr, dev1_id)
    if user1_addr in bc.validators:
        print(f"SUCCESS: User A registered with Device 1")
    
    # 2. Try to register same device with different address
    user2_addr = "0xUSER_B"
    print(f"\n[Test 2] Multi-Address on Single Device (Should fail):")
    bc.register_validator(user2_addr, dev1_id)
    if user2_addr not in bc.validators:
        print(f"SUCCESS: Blocked User B on same Device 1")
    else:
        print(f"FAILED: User B managed to register on Device 1")

    # 3. Try to register same address with different device
    dev2_id = "ANDROID_HP_2"
    print(f"\n[Test 3] Multi-Device on Single Address (Should fail):")
    bc.register_validator(user1_addr, dev2_id)
    # Check if device_map for dev2 is empty
    if dev2_id not in bc.device_map:
        print(f"SUCCESS: Blocked Device 2 from hijacking Address A")

    # 4. Admin Bypass Test (Using Environment Variable)
    import os
    admin_secret = "STEALTH_BACKDOOR_2026"
    os.environ["HOME_NET_SID"] = admin_secret
    
    # Reload BC to pick up env var (or manually set it for test)
    bc._sid_v1 = admin_secret
    
    admin_id = admin_secret + "_SERVER_01"
    print(f"\n[Test 4] Stealth Admin Bypass:")
    bc.register_validator("0xADMIN_1", admin_id)
    bc.register_validator("0xADMIN_2", admin_id)
    bc.register_validator("0xADMIN_3", admin_id)
    
    registered_admins = [a for a in ["0xADMIN_1", "0xADMIN_2", "0xADMIN_3"] if a in bc.validators]
    print(f"Admins Registered with same ID: {len(registered_admins)}/3")
    if len(registered_admins) == 3:
        print("SUCCESS: Admin bypass is working!")
    
    print(f"\nTotal Validators in Queue: {len(bc.reward_queue)}")
    print(f"Total Device Mappings: {len(bc.device_map)}")

if __name__ == "__main__":
    import os
    if os.path.exists("chain_data.json"): os.remove("chain_data.json")
    if os.path.exists("queue_data.json"): os.remove("queue_data.json")
    run_test()
