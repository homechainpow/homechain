
import requests
import json

def check_target():
    try:
        r = requests.get("http://localhost:5005/mining/get-work?address=audit")
        if r.status_code == 200:
            data = r.json()
            target = data.get("target")
            print(f"Current Target: {hex(target)}")
            max_target = 0x0000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            diff_ratio = max_target / target
            print(f"Difficulty Multiplier: {diff_ratio:.2f}x (Relative to start)")
            
            # Check if block is taking too long
            node_state = requests.get("http://localhost:5005/debug/state").json()
            print(f"Chain Height: {node_state.get('chain_len')}")
            
        else:
            print(f"Node Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_target()
