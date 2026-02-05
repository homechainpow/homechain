import hashlib
import json
import time
from ecdsa import SigningKey, SECP256k1, VerifyingKey
import binascii

class Transaction:
    def __init__(self, sender: str, receiver: str, amount: int, data: dict = None, signature: str = None, timestamp: float = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.data = data or {}
        self.timestamp = timestamp or time.time()
        self.signature = signature

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "data": self.data,
            "timestamp": self.timestamp,
            "signature": self.signature
        }

    def compute_hash(self) -> str:
        """Computes the hash of the transaction (excluding signature)."""
        tx_dict = self.to_dict()
        del tx_dict["signature"]
        tx_string = json.dumps(tx_dict, sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()

    def sign(self, private_key: SigningKey):
        """Signs the transaction using the sender's private key."""
        tx_hash = self.compute_hash()
        signature = private_key.sign(tx_hash.encode()).hex()
        self.signature = signature

    def is_valid(self) -> bool:
        """Verifies the transaction signature."""
        if self.sender == "SYSTEM":  # System transactions (e.g. block rewards)
            return True
        
        if not self.signature:
            return False

        try:
            public_key_bytes = binascii.unhexlify(self.sender)
            vk = VerifyingKey.from_string(public_key_bytes, curve=SECP256k1)
            tx_hash = self.compute_hash()
            return vk.verify(binascii.unhexlify(self.signature), tx_hash.encode())
        except Exception:
            return False

class Wallet:
    def __init__(self):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.verifying_key
        self.address = self.public_key.to_string().hex()

    def sign_transaction(self, transaction: Transaction):
        if transaction.sender != self.address:
            raise ValueError("You can only sign transactions sent from your address.")
        transaction.sign(self.private_key)

    @staticmethod
    def generate_dummy_wallet():
        """Generates a wallet for testing purposes."""
        return Wallet()
