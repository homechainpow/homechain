from blockchain import Blockchain, Block
from wallet import Transaction, Wallet
import json
import time

def run_test():
    print("--- STARTING SOCIALIZED REWARD SIMULATION ---")
    bc = Blockchain()
    
    # 1. Generate 150 local wallets and register them
    wallets = [Wallet() for _ in range(150)]
    addresses = [w.address for w in wallets]
    print(f"Generated {len(addresses)} test validators.")
    
    for addr in addresses:
        bc.register_validator(addr)
    print(f"Registered {len(bc.validators)} validators in the node.")

    # 2. Mine Block 1 found by Validator 0
    from consensus import ProofOfWork
    last_block = bc.get_last_block()
    index = last_block.index + 1
    prev_hash = last_block.hash
    timestamp = time.time()
    validator = addresses[0]
    txs_json = json.dumps([], sort_keys=True)
    
    print(f"Mining Block {index}...")
    nonce, block_hash = ProofOfWork.mine(index, prev_hash, timestamp, txs_json, validator, bc.target)
    
    block_1_data = {
        "index": index,
        "timestamp": timestamp,
        "transactions": [],
        "previous_hash": prev_hash,
        "validator": validator,
        "nonce": nonce,
        "target": bc.target,
        "hash": block_hash
    }
    
    if bc.submit_block(block_1_data):
        print("Block 1 Accepted!")
    else:
        print("Block 1 Rejected!")
        return

    # Check rewards for Block 1
    last_block = bc.get_last_block()
    finder_reward = [r for r in last_block.rewards if r.data.get('type') == 'reward_finder']
    bonus_rewards = [r for r in last_block.rewards if r.data.get('type') == 'reward_bonus']
    
    print(f"\nBlock 1 Summary:")
    print(f"- Recipients: {len(last_block.rewards)}")
    print(f"- Finder: {finder_reward[0].receiver[:10]}... ({finder_reward[0].amount})")
    print(f"- Bonus Recipients: {len(bonus_rewards)}")

    # 3. Mine Block 2 found by Validator 0 again
    last_block = bc.get_last_block()
    index = last_block.index + 1
    prev_hash = last_block.hash
    timestamp = time.time()
    
    print(f"\nMining Block {index}...")
    nonce, block_hash = ProofOfWork.mine(index, prev_hash, timestamp, txs_json, validator, bc.target)
    
    block_2_data = {
        "index": index,
        "timestamp": timestamp,
        "transactions": [],
        "previous_hash": prev_hash,
        "validator": validator,
        "nonce": nonce,
        "target": bc.target,
        "hash": block_hash
    }
    
    if bc.submit_block(block_2_data):
        print("Block 2 Accepted!")
    
    last_block = bc.get_last_block()
    bonus_rewards_2 = [r for r in last_block.rewards if r.data.get('type') == 'reward_bonus']
    print(f"Block 2 Bonus Recipients: {len(bonus_rewards_2)}")

    # 4. Check Queue Fairness
    b1_recipients = set([r.receiver for r in bonus_rewards])
    b2_recipients = set([r.receiver for r in bonus_rewards_2])
    
    overlap = b1_recipients.intersection(b2_recipients)
    print(f"Overlap between Block 1 and Block 2 recipients: {len(overlap)}")
    
    if len(overlap) == 0 and len(b2_recipients) > 0:
        print("SUCCESS: Fairness queue is circulating correctly (Round Robin)!")
    else:
        print(f"NOTE: Overlap found or empty pool. (Overlap: {len(overlap)})")

    # 5. Check Balances
    test_addr = list(b1_recipients)[0]
    balance = bc.get_balance(test_addr)
    print(f"\nBalance Check for {test_addr[:10]}...: {balance} $HOME")
    
if __name__ == "__main__":
    import os
    if os.path.exists("chain_data.json"): os.remove("chain_data.json")
    if os.path.exists("queue_data.json"): os.remove("queue_data.json")
    run_test()
