import hashlib
import json

class ProofOfWork:
    # Max target corresponds to absolute minimum difficulty
    # This is a 256-bit number. 
    # Let's start with something reasonable: about 4 leading hex zeros.
    MAX_TARGET = 0x0000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    @staticmethod
    def calculate_hash(index, previous_hash, timestamp, transactions, validator, nonce):
        data_string = f"{index}{previous_hash}{timestamp}{transactions}{validator}{nonce}"
        return hashlib.sha256(data_string.encode()).hexdigest()

    @staticmethod
    def is_valid_proof(block_hash, target):
        """
        Check if block hash is below target threshold.
        """
        return int(block_hash, 16) < target

    @staticmethod
    def mine(index, previous_hash, timestamp, transactions, validator, target):
        nonce = 0
        while True:
            hash_result = ProofOfWork.calculate_hash(index, previous_hash, timestamp, transactions, validator, nonce)
            if int(hash_result, 16) < target:
                return nonce, hash_result
            nonce += 1
