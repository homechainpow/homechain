import sqlite3
import requests

# Supabase credentials
SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def is_valid_hex_address(addr):
    """Validate that address is a proper 128-character hex string."""
    if not addr or len(addr) != 128:
        return False
    try:
        int(addr, 16)
        return True
    except (ValueError, TypeError):
        return False

def force_resync_holders():
    """Force re-sync all holders from local DB to Supabase with validation."""
    print("=" * 60)
    print("Force Re-sync Holders with Address Validation")
    print("=" * 60)
    
    # 1. Get all balances from local DB
    print("\n[*] Reading balances from local chain_v2.db...")
    conn = sqlite3.connect('chain_v2.db')
    c = conn.cursor()
    c.execute("SELECT address, balance FROM balances ORDER BY balance DESC")
    all_balances = c.fetchall()
    conn.close()
    
    print(f"[✓] Found {len(all_balances)} addresses in local DB")
    
    # 2. Filter valid addresses only
    valid_holders = []
    invalid_count = 0
    
    for addr, balance in all_balances:
        if is_valid_hex_address(addr):
            valid_holders.append({"address": addr, "balance": int(balance)})
        else:
            invalid_count += 1
            print(f"[!] Skipping invalid address: {addr}")
    
    print(f"\n[✓] Valid addresses: {len(valid_holders)}")
    print(f"[!] Invalid addresses skipped: {invalid_count}")
    
    if not valid_holders:
        print("\n[!] No valid holders to sync!")
        return
    
    # 3. Clear existing holders table in Supabase
    print(f"\n[*] Clearing existing holders table in Supabase...")
    try:
        del_res = requests.delete(
            f"{SB_URL}/rest/v1/holders?address=neq.PLACEHOLDER",
            headers=headers
        )
        if del_res.status_code in [200, 204]:
            print("[✓] Holders table cleared")
        else:
            print(f"[!] Clear failed: {del_res.status_code}")
    except Exception as e:
        print(f"[!] Clear error: {e}")
    
    # 4. Batch insert valid holders
    print(f"\n[*] Syncing {len(valid_holders)} valid holders to Supabase...")
    
    batch_size = 100
    synced = 0
    
    for i in range(0, len(valid_holders), batch_size):
        batch = valid_holders[i:i+batch_size]
        try:
            res = requests.post(
                f"{SB_URL}/rest/v1/holders",
                headers=headers,
                json=batch
            )
            if res.status_code in [200, 201, 204]:
                synced += len(batch)
                print(f"[✓] Synced {synced}/{len(valid_holders)} holders...", end="\r")
            else:
                print(f"\n[!] Batch {i//batch_size + 1} failed: {res.status_code}")
        except Exception as e:
            print(f"\n[!] Batch {i//batch_size + 1} error: {e}")
    
    print(f"\n\n[✓] Successfully synced {synced} valid holders to Supabase!")
    print("\n" + "=" * 60)
    print("RE-SYNC COMPLETE!")
    print("=" * 60)
    print(f"\n✅ {synced} valid HEX addresses synced")
    print(f"❌ {invalid_count} invalid addresses skipped")
    print("\nScanner should now show only valid wallet addresses!")

if __name__ == "__main__":
    force_resync_holders()
