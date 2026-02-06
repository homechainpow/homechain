
import os
from ecdsa import SigningKey, SECP256k1

TARGET_DIR = r"C:\Users\Administrator\Downloads\VIP_WEALTH"
OUTPUT_FILE = r"C:\Users\Administrator\Desktop\vip_wealth_addresses.txt"

def extract_addresses():
    if not os.path.exists(TARGET_DIR):
        print(f"Directory not found: {TARGET_DIR}")
        return

    print(f"Scanning PEMs in: {TARGET_DIR}")
    all_files = os.listdir(TARGET_DIR)
    pem_files = [f for f in all_files if f.lower().endswith(".pem")]
    print(f"Found {len(pem_files)} PEM files.")
    
    addresses = []
    
    for f in pem_files:
        try:
            with open(os.path.join(TARGET_DIR, f), 'rb') as fp:
                pem_data = fp.read()
                try:
                    sk = SigningKey.from_pem(pem_data)
                    vk = sk.verifying_key
                    # Match wallet.py logic: public_key.to_string().hex()
                    address = vk.to_string().hex()
                    addresses.append(address)
                except Exception as e:
                    # Try reading as string if binary load fails or format differs
                    print(f"Failed to load PEM {f}: {e}")
        except Exception as e:
            print(f"Error reading file {f}: {e}")
            
    with open(OUTPUT_FILE, 'w') as out:
        for addr in addresses:
            out.write(addr + "\n")
            
    print(f"Extracted {len(addresses)} addresses to {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_addresses()
