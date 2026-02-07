from blockchain import Blockchain
from wallet import Transaction
import os

def test():
    db = 'chain_v2.db'
    if os.path.exists(db): os.remove(db)
    
    print("--- Phase 1: Create Chain ---")
    bc = Blockchain()
    sys_bal = bc.get_balance("SYSTEM")
    print(f"Genesis System Balance: {sys_bal}")
    
    tx = Transaction("SYSTEM", "ADDR_1", 1000, 0)
    bc.add_transaction(tx)
    
    # Manually trigger a block to check state update
    print("--- Phase 2: Submit Block ---")
    last = bc.get_last_block()
    from blockchain import Block
    nb = Block(1, [tx], last.hash, "MINER", timestamp=1700000001)
    bc.chain.append(nb)
    bc.update_state(nb)
    print(f"Post-Submit ADDR_1 Balance: {bc.get_balance('ADDR_1')}")
    bc.save_chain()
    
    print("--- Phase 3: Reload Chain ---")
    bc2 = Blockchain()
    print(f"Reloaded ADDR_1 Balance: {bc2.get_balance('ADDR_1')}")

if __name__ == "__main__":
    test()
