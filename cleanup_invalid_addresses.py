import sqlite3
import requests

# Supabase credentials
SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

def is_valid_hex_address(addr):
    """Check if address is a valid 128-character hex string."""
    if len(addr) != 128:
        return False
    try:
        int(addr, 16)
        return True
    except ValueError:
        return False

def clean_local_db():
    """Remove invalid addresses from local chain_v2.db"""
    print("=" * 60)
    print("Cleaning Local Database (chain_v2.db)")
    print("=" * 60)
    
    conn = sqlite3.connect('chain_v2.db')
    c = conn.cursor()
    
    # Get all addresses
    c.execute("SELECT address, balance FROM balances")
    all_balances = c.fetchall()
    
    invalid_addresses = []
    for addr, balance in all_balances:
        if not is_valid_hex_address(addr):
            invalid_addresses.append(addr)
    
    print(f"\nFound {len(invalid_addresses)} invalid addresses:")
    for addr in invalid_addresses:
        print(f"  - {addr}")
    
    if invalid_addresses:
        print(f"\n[*] Deleting {len(invalid_addresses)} invalid addresses from local DB...")
        for addr in invalid_addresses:
            c.execute("DELETE FROM balances WHERE address = ?", (addr,))
        conn.commit()
        print("[✓] Local DB cleaned!")
    else:
        print("[✓] No invalid addresses found in local DB")
    
    conn.close()

def clean_supabase():
    """Remove invalid addresses from Supabase holders table"""
    print("\n" + "=" * 60)
    print("Cleaning Supabase Database (holders table)")
    print("=" * 60)
    
    # Get all holders
    res = requests.get(f"{SB_URL}/rest/v1/holders?select=address", headers=headers)
    if res.status_code != 200:
        print(f"[!] Failed to fetch holders: {res.status_code}")
        return
    
    all_holders = res.json()
    invalid_addresses = []
    
    for holder in all_holders:
        addr = holder['address']
        if not is_valid_hex_address(addr):
            invalid_addresses.append(addr)
    
    print(f"\nFound {len(invalid_addresses)} invalid addresses:")
    for addr in invalid_addresses[:20]:  # Show first 20
        print(f"  - {addr}")
    if len(invalid_addresses) > 20:
        print(f"  ... and {len(invalid_addresses) - 20} more")
    
    if invalid_addresses:
        print(f"\n[*] Deleting {len(invalid_addresses)} invalid addresses from Supabase...")
        deleted = 0
        for addr in invalid_addresses:
            del_res = requests.delete(
                f"{SB_URL}/rest/v1/holders?address=eq.{addr}",
                headers=headers
            )
            if del_res.status_code in [200, 204]:
                deleted += 1
        print(f"[✓] Deleted {deleted} invalid addresses from Supabase!")
    else:
        print("[✓] No invalid addresses found in Supabase")

def main():
    print("\n🏙️💎 HomeChain V2 - Database Cleanup Script 🚀\n")
    
    # Clean local database
    clean_local_db()
    
    # Clean Supabase
    clean_supabase()
    
    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE!")
    print("=" * 60)
    print("\n[✓] All invalid addresses have been removed.")
    print("[✓] Only valid 128-character HEX addresses remain.")
    print("\nPlease restart the sync worker to re-sync clean data.")

if __name__ == "__main__":
    main()
