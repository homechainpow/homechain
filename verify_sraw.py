from blockchain import Blockchain
from wallet import Transaction
import os
import math

def test_sraw_distribution():
    print("--- Phase 1: Setup Multi-Miner Economy ---")
    db = 'chain_v2.db'
    if os.path.exists(db): os.remove(db)
    
    bc = Blockchain()
    
    # Simulate 3 Miners with different activity levels
    # Miner 1: Very Active (100 polls)
    # Miner 2: Normal (25 polls)
    # Miner 3: Occasional (4 polls)
    
    for _ in range(100): bc.record_activity("MINER_1")
    for _ in range(25): bc.record_activity("MINER_2")
    for _ in range(4): bc.record_activity("MINER_3")
    
    print("[*] Activity Recorded.")
    
    # Miner 1 finds the block
    print("--- Phase 2: Block Submission (Miner 1 Wins) ---")
    last = bc.get_last_block()
    from blockchain import Block
    nb = Block(1, [], last.hash, "MINER_1", timestamp=1700000001)
    
    # Manually execute the reward logic via submit_block logic 
    # (Since we want to verify the internal distribution)
    bc.submit_block(nb.to_dict())
    
    # Calculate expected weights:
    # W1 = sqrt(100) = 10
    # W2 = sqrt(25) = 5
    # W3 = sqrt(4) = 2
    # Total W = 17
    
    bal1 = bc.get_balance("MINER_1")
    bal2 = bc.get_balance("MINER_2")
    bal3 = bc.get_balance("MINER_3")
    
    print(f"[*] Miner 1 (Winner) Balance: {bal1 / 10**8} $HOME (Raw: {bal1})")
    print(f"[*] Miner 2 (Active) Balance: {bal2 / 10**8} $HOME (Raw: {bal2})")
    print(f"[*] Miner 3 (Light) Balance: {bal3 / 10**8} $HOME (Raw: {bal3})")
    
    if bal2 > bal3 and bal1 > bal2:
        print("\n[SUCCESS] SRAW COMMUNITY ENGINE VERIFIED!")
    else:
        print("\n[FAILURE] Reward distribution calculation error.")
        print(f"Logic Status: bal2 > bal3: {bal2 > bal3}, bal1 > bal2: {bal1 > bal2}")

if __name__ == "__main__":
    test_sraw_distribution()
