
import requests
import json

def check_target_full():
    try:
        r = requests.get("http://localhost:5005/mining/get-work?address=audit")
        if r.status_code == 200:
            data = r.json()
            target = data.get("target")
            print(f"Target (Hex): {hex(target)}")
            print(f"Target (Len): {len(hex(target))}")
            
            # Max Target
            max_target = 0x0000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            print(f"Max Target (Hex): {hex(max_target)}")
            
            if target < max_target:
                print(f"Status: HARDER than baseline.")
            else:
                print(f"Status: EASIER than baseline (capped at MAX).")
                
            # Check last block hash
            state = requests.get("http://localhost:5005/debug/state").json()
            chain_len = state.get("chain_len")
            last_block = requests.get(f"http://localhost:5005/block/{chain_len-1}").json()
            print(f"Last Block Index: {last_block['index']}")
            print(f"Last Block Target: {hex(last_block.get('target', 0))}")
            print(f"Last Block Hash: {last_block['hash']}")
            
        else:
            print(f"Error: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_target_full()
