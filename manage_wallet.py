import argparse
import os
from ecdsa import SigningKey, SECP256k1
import binascii

WALLET_FILE = "my_wallet.pem"

def create_wallet(filename=WALLET_FILE):
    if os.path.exists(filename):
        print(f"⚠️  Wallet file '{filename}' already exists!")
        choice = input("Overwrite? (y/N): ")
        if choice.lower() != 'y':
            return
    
    # Generate Key
    sk = SigningKey.generate(curve=SECP256k1)
    pem = sk.to_pem()
    
    with open(filename, "wb") as f:
        f.write(pem)
        
    vk = sk.verifying_key
    address = vk.to_string().hex()
    
    print(f"✅ New Wallet Created!")
    print(f"📁 Saved to: {os.path.abspath(filename)}")
    print(f"🔑 Address: {address}")
    print("KEEP THIS FILE SAFE! Anyone with this file can spend your $HOME.")

def load_wallet(filename=WALLET_FILE):
    if not os.path.exists(filename):
        print(f"❌ Wallet file '{filename}' not found.")
        return None, None

    with open(filename, "rb") as f:
        pem = f.read()
        
    sk = SigningKey.from_pem(pem)
    vk = sk.verifying_key
    address = vk.to_string().hex()
    
    print(f"🔓 Wallet Loaded: {filename}")
    print(f"🔑 Address: {address}")
    return sk, address

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HomeChain Wallet Manager")
    parser.add_argument('action', choices=['create', 'show'], help='Action to perform')
    parser.add_argument('--file', default=WALLET_FILE, help='Wallet file path')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        create_wallet(args.file)
    elif args.action == 'show':
        load_wallet(args.file)
