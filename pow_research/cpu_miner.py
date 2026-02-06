import hashlib
import time

def mine(block_number, transactions, previous_hash, difficulty=4):
    """
    Simulates Real CPU Mining.
    difficulty: number of leading zeros required in hash.
    """
    prefix_str = '0' * difficulty
    nonce = 0
    start = time.time()
    
    print(f"Mining Block {block_number} with difficulty {difficulty}...")
    
    while True:
        # Create block content string
        block_content = f"{block_number}{transactions}{previous_hash}{nonce}"
        hash_result = hashlib.sha256(block_content.encode()).hexdigest()
        
        if hash_result.startswith(prefix_str):
            end = time.time()
            print(f"\nSUCCESS! Nonce used: {nonce}")
            print(f"Hash: {hash_result}")
            print(f"Time Taken: {end - start:.4f} seconds")
            print(f"Hashrate: {nonce / (end-start):.2f} H/s")
            return nonce, hash_result
        
        nonce += 1

# Test it
if __name__ == "__main__":
    mine(1, "tx_data", "0000abc", difficulty=4) # Try difficulty 4, 5, 6 to see CPU load
