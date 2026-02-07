import sqlite3
import os

def diagnose():
    db_path = 'chain_v2.db'
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Active Miners
    print("--- Most Active Miners (Last 10) ---")
    cur.execute("SELECT address, poll_count, last_poll FROM miner_activity ORDER BY last_poll DESC LIMIT 10")
    for row in cur.fetchall():
        print(f"Address: {row[0]} | Polls: {row[1]} | Last Seen: {row[2]}")
        
    # 2. Top Balances
    print("\n--- Top Balances ---")
    cur.execute("SELECT address, balance FROM balances ORDER BY balance DESC LIMIT 10")
    for row in cur.fetchall():
        print(f"Address: {row[0]} | Balance: {row[1] / 10**8:.2f} HOME")
        
    conn.close()

if __name__ == "__main__":
    diagnose()
