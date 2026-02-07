import sqlite3

try:
    conn = sqlite3.connect('chain_v2.db')
    c = conn.cursor()
    
    # 1. Total Supply
    c.execute('SELECT SUM(balance) FROM balances')
    total = c.fetchone()[0] or 0
    print(f"TOTAL_SUPPLY_SAT: {total}")
    print(f"TOTAL_SUPPLY_HOME: {total/10**8:.8f}")
    
    # 2. Top Holders (> 10,000 HOME)
    print("\n--- Top Holders (> 10,000 HOME) ---")
    c.execute('SELECT address, balance FROM balances WHERE balance > 1000000000000 ORDER BY balance DESC')
    rows = c.fetchall()
    for addr, bal in rows:
        print(f"{addr}: {bal/10**8:.8f}")
        
    # 3. Check specific names
    print("\n--- Specific Labels ---")
    for name in ["S_1", "S_901", "SYSTEM", "GENESIS", "M1", "M2", "M3"]:
        c.execute('SELECT balance FROM balances WHERE address = ?', (name,))
        row = c.fetchone()
        if row:
            print(f"{name}: {row[0]/10**8:.8f}")
        else:
            print(f"{name}: NOT FOUND")
            
    conn.close()
except Exception as e:
    print(f"Error: {e}")
