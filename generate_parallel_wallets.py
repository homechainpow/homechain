from ecdsa import SigningKey, SECP256k1
import os

def generate_wallets(count=10, directory="wallets"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for i in range(1, count + 1):
        filename = f"p{i}.pem"
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            print(f"Wallet {path} already exists, skipping.")
            continue
            
        sk = SigningKey.generate(curve=SECP256k1)
        with open(path, "wb") as f:
            f.write(sk.to_pem())
        print(f"Generated {path}")

if __name__ == "__main__":
    generate_wallets()
