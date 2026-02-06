
import requests
import json

BASE_URL = "http://localhost:5005"

def test():
    print("--- Verifying P2P Nodes ---")
    reg_data = {"address": "http://13.220.55.223:5005"}
    r = requests.post(f"{BASE_URL}/nodes/register", json=reg_data)
    print(f"[*] Register Node: {r.status_code} - {r.json()}")
    
    r = requests.get(f"{BASE_URL}/nodes")
    print(f"[*] Known Nodes: {r.json()}")

    print("\n--- Verifying Fee Enforcement ---")
    # Funded address (Miner 1)
    funded_addr = "7c2b0e66dceacc3c50410a2abb97a7067a43c231b897633458514930d4f07ba6"
    
    tx_low = {
        "sender": funded_addr,
        "receiver": "GENESIS",
        "amount": 1,
        "fee": 1000  # Too low
    }
    r = requests.post(f"{BASE_URL}/transactions/new", json=tx_low)
    print(f"[*] Submit Low Fee TX (Expect 400): {r.status_code} - {r.text}")

    # Correct fee
    tx_ok = {
        "sender": funded_addr,
        "receiver": "GENESIS",
        "amount": 1,
        "fee": 1000000  # 0.01 HOME
    }
    # Note: This might fail balance check but we want to see FEE check first
    r = requests.post(f"{BASE_URL}/transactions/new", json=tx_ok)
    print(f"[*] Submit Correct Fee TX (Expect success or balance err): {r.status_code} - {r.text}")

if __name__ == "__main__":
    test()
