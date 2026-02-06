
import os
import json

TARGET_DIR = r"C:\Users\Administrator\Downloads\VIP_WEALTH"
OUTPUT_FILE = r"C:\Users\Administrator\Desktop\vip_wealth_addresses.txt"

def extract_addresses():
    if not os.path.exists(TARGET_DIR):
        print(f"Directory not found: {TARGET_DIR}")
        return

    addresses = []
    files = [f for f in os.listdir(TARGET_DIR) if f.endswith(".json")]
    
    print(f"Found {len(files)} JSON files.")
    
    for f in files:
        try:
            with open(os.path.join(TARGET_DIR, f), 'r') as fp:
                data = json.load(fp)
                if "address" in data:
                    addresses.append(data["address"])
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    with open(OUTPUT_FILE, 'w') as out:
        for addr in addresses:
            out.write(addr + "\n")
            
    print(f"Extracted {len(addresses)} addresses to {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_addresses()
