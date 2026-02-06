
import sys
import os

# Add local dir to path
sys.path.append('.')

from blockchain import Blockchain

def audit():
    print("=== Internal Balance Audit ===")
    bc = Blockchain()
    print(f"[*] Chain Length: {len(bc.chain)}")
    print(f"[*] Balances Count: {len(bc.balances)}")
    
    m1_addr = "ce816a27420c956635cf92484e28b197fed3013"
    m1_bal = bc.balances.get(m1_addr, "MISSING")
    print(f"[*] Miner 1 ({m1_addr}) Balance: {m1_bal}")
    
    # Check lowercase vs uppercase
    m1_upper = m1_addr.upper()
    print(f"[*] Miner 1 (UPPER) Balance: {bc.balances.get(m1_upper, 'MISSING')}")

    # Sort and show top 10
    sorted_bals = sorted(bc.balances.items(), key=lambda x: x[1], reverse=True)
    print("[*] Top 10 Balances (Full):")
    for addr, bal in sorted_bals[:10]:
        print(f"  {addr}: {bal} (HOME: {bal/100_000_000:.2f})")

if __name__ == "__main__":
    audit()
