import hashlib
import json

class ProofOfWork:
    # Max target corresponds to absolute minimum difficulty
    # This is a 256-bit number. 
    # Let's start with something reasonable: about 4 leading hex zeros.
    MAX_TARGET = 0x0000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    @staticmethod
    def calculate_merkle_root(transactions: list) -> str:
        """
        Calculates the Merkle Root hash of a list of transactions.
        If the list is empty, returns a zero hash.
        """
        if not transactions:
            return "0" * 64
        
        # 1. Start with the hash of each transaction dict
        hashes = [hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest() for tx in transactions]
        
        # 2. Iterate until we have only one hash (the root)
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1]) # Duplicate last element if odd
            
            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i+1]
                new_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = new_hashes
            
        return hashes[0]

    @staticmethod
    def calculate_hash(index, previous_hash, timestamp, merkle_root, validator, nonce):
        """
        Optimized V2 Hash: Uses Merkle Root instead of full transaction list.
        """
        data_string = f"{index}{previous_hash}{timestamp}{merkle_root}{validator}{nonce}"
        return hashlib.sha256(data_string.encode()).hexdigest()

    @staticmethod
    def is_valid_proof(block_hash, target):
        return int(block_hash, 16) < target

    @staticmethod
    def mine(index, previous_hash, timestamp, merkle_root, validator, target):
        nonce = 0
        while True:
            hash_result = ProofOfWork.calculate_hash(index, previous_hash, timestamp, merkle_root, validator, nonce)
            if int(hash_result, 16) < target:
                return nonce, hash_result
            nonce += 1
