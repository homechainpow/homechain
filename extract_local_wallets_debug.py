
import os
import json

TARGET_DIR = r"C:\Users\Administrator\Downloads\VIP_WEALTH"
OUTPUT_FILE = r"C:\Users\Administrator\Desktop\vip_wealth_addresses.txt"

def extract_addresses():
    if not os.path.exists(TARGET_DIR):
        print(f"Directory not found: {TARGET_DIR}")
        return

    print(f"Scanning: {TARGET_DIR}")
    all_files = os.listdir(TARGET_DIR)
    print(f"Total entries in dir: {len(all_files)}")
    print(f"First 10 entries: {all_files[:10]}")
    
    addresses = []
    
    # Check for PEMs too just in case
    # If they are PEMs, we likely can't derive address easily without library?
    # Or maybe the key is inside?
    # But user said check folder.
    
    json_files = [f for f in all_files if f.lower().endswith(".json")]
    print(f"JSON Files found: {len(json_files)}")
    
    for f in json_files:
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
