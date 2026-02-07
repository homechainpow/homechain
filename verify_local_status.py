import sqlite3
import os

def check_local():
    db = 'chain_v2.db'
    if not os.path.exists(db):
        print("chain_v2.db not found")
        return
    
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    
    # 1. Blocks
    cur.execute("SELECT count(*) FROM blocks")
    count = cur.fetchone()[0]
    print(f"Total Blocks: {count}")
    
    # 2. M2/M3 Check
    m2_hex = "01fbb49a2a9bbb6cb7b0034a7873497d39462615bc0fd9be4e8533c7a4966a3d"
    m3_hex = "04feaa27529d23357a829f07474476686a7d743a677b47423e20251759491696"
    
    print("\n--- Miner Balance Check ---")
    for addr in [m2_hex, m3_hex]:
        cur.execute("SELECT balance FROM balances WHERE address = ?", (addr,))
        row = cur.fetchone()
        name = "M2" if addr == m2_hex else "M3"
        if row:
            print(f"{name} ({addr[:10]}...): {row[0] / 10**8:.2f} HOME")
        else:
            print(f"{name} ({addr[:10]}...): NOT FOUND")
            
    # 3. Check for leftover strings
    print("\n--- Checking for Literal String Labels ---")
    cur.execute("SELECT address, balance FROM balances WHERE address IN ('M2', 'M3')")
    leftovers = cur.fetchall()
    if leftovers:
        for row in leftovers:
            print(f"WARNING: Leftover label {row[0]} with balance {row[1]}")
    else:
        print("Success: No leftover M2/M3 literal labels found.")
        
    conn.close()

if __name__ == "__main__":
    check_local()
