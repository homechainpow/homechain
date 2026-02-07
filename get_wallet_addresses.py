from ecdsa import SigningKey
import os
import glob

def get_addresses():
    wallet_dir = r"C:\Users\Administrator\.gemini\antigravity\scratch\HomeChain\wallets"
    pem_files = glob.glob(os.path.join(wallet_dir, "*.pem"))
    
    print(f"Found {len(pem_files)} pem files.")
    for pem_file in pem_files:
        try:
            with open(pem_file, "rb") as f:
                pem = f.read()
            sk = SigningKey.from_pem(pem)
            vk = sk.verifying_key
            address = vk.to_string().hex()
            basename = os.path.basename(pem_file)
            print(f"{basename}: {address}")
        except Exception as e:
            # print(f"Error reading {pem_file}: {e}")
            pass

if __name__ == "__main__":
    get_addresses()
