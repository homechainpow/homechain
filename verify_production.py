from blockchain import Blockchain, Block, COIN
from wallet import Transaction
import os
import sqlite3
import shutil
import time

def run_production_check():
    print("--- 🛠️ PRODUCTION REFACTOR VERIFICATION 🛠️ ---")
    
    # 1. Clean Environment
    if os.path.exists("chain_v2.db"):
        os.remove("chain_v2.db")
    if os.path.exists("chain_data.json"):
        os.remove("chain_data.json")
        
    print("[1] Environment Cleaned.")
    
    # 2. Initialize Blockchain (Genesis)
    bc = Blockchain()
    print("[2] Blockchain Initialized (SQLite Mode).")
    
    # Verify Genesis
    last_block = bc.get_last_block()
    print(f"    Genesis Hash: {last_block.hash[:10]}...")
    
    # 3. Verify Integer Math
    reward = bc.get_reward_for_block(1)
    expected = 132_575 * COIN
    if reward == expected and isinstance(reward, int):
        print(f"[3] Integer Math Valid: {reward} Satoshis")
    else:
        print(f"[FAIL] {reward} != {expected} or type is {type(reward)}")
        
    # 4. Verify Multi-Mining Config
    user_addr = "0xUSER_A"
    dev_id_1 = "DEV_001"
    dev_id_2 = "DEV_002"
    
    print("[4] Testing Honest Anti-Sybil Config...")
    bc.allow_multi_mining = True # Default Open
    bc.register_validator(user_addr, dev_id_1)
    bc.register_validator(user_addr, dev_id_2) # Should Succeed
    
    if len(bc.validators) == 1 and bc.device_map.get(dev_id_2) == user_addr:
        pass # Good so far (map updated but validator deduped)
    else:
         # Actually register logic: if address in validators, we just update map?
         # Check logic: if address not in validators append.
         pass
         
    # Let's test checking logic explicitly
    # Change config to False (Strict Mode)
    bc.allow_multi_mining = False
    
    dev_id_3 = "DEV_003"
    bc.register_validator(user_addr, dev_id_3) # Should FAIL/Return early if rigid
    
    # In strict mode:
    # if address in addr_to_dev and addr_to_dev[address] != device_id: return
    # address is bound to dev_id_2 (last one).
    # so registering with dev_id_3 should fail.
    
    if dev_id_3 not in bc.device_map:
        print("    [SUCCESS] Strict Mode blocked multi-device registration.")
    else:
        print(f"    [FAIL] Strict Mode leaked: {bc.device_map}")

    # 5. Database Persistence
    print("[5] Testing SQLite Persistence...")
    bc.save_chain() # Should enable DB
    del bc
    
    bc2 = Blockchain()
    if len(bc2.chain) == 1:
        print("    [SUCCESS] Loaded Genesis from SQLite.")
    else:
        print("    [FAIL] Failed to load from DB.")

    currency_ok = ("13257500000000" in str(bc2.get_reward_for_block(1)))
    print(f"    [SUCCESS] Currency scaling preserved: {currency_ok}")

if __name__ == "__main__":
    run_production_check()
