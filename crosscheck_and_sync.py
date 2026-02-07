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

print("=" * 70)
print("CROSS-CHECK: Local DB vs Supabase")
print("=" * 70)

# 1. Get all addresses from local DB
conn = sqlite3.connect('chain_v2.db')
c = conn.cursor()
c.execute("SELECT address, balance FROM balances ORDER BY balance DESC")
local_holders = {row[0]: int(row[1]) for row in c.fetchall()}
conn.close()

print(f"\n[LOCAL DB]")
print(f"  Total addresses: {len(local_holders)}")
print(f"  Total supply: {sum(local_holders.values())/100000000:.2f} HOME")

# 2. Get all addresses from Supabase
try:
    res = requests.get(
        f"{SB_URL}/rest/v1/holders?select=address,balance",
        headers=headers
    )
    if res.status_code == 200:
        sb_holders = {h['address']: int(h['balance']) for h in res.json()}
        print(f"\n[SUPABASE]")
        print(f"  Total addresses: {len(sb_holders)}")
        print(f"  Total supply: {sum(sb_holders.values())/100000000:.2f} HOME")
    else:
        print(f"\n[!] Failed to fetch Supabase holders: {res.status_code}")
        sb_holders = {}
except Exception as e:
    print(f"\n[!] Error fetching Supabase: {e}")
    sb_holders = {}

# 3. Find missing addresses
missing_addresses = set(local_holders.keys()) - set(sb_holders.keys())
missing_supply = sum(local_holders[addr] for addr in missing_addresses)

print(f"\n[MISSING FROM SUPABASE]")
print(f"  Missing addresses: {len(missing_addresses)}")
print(f"  Missing supply: {missing_supply/100000000:.2f} HOME")

if missing_addresses:
    print(f"\n  Top 10 missing wallets:")
    sorted_missing = sorted(missing_addresses, key=lambda a: local_holders[a], reverse=True)
    for i, addr in enumerate(sorted_missing[:10]):
        balance = local_holders[addr]
        print(f"    {i+1}. {addr[:16]}...{addr[-8:]} = {balance/100000000:.4f} HOME")

# 4. Sync missing addresses
if missing_addresses:
    print(f"\n[*] Syncing {len(missing_addresses)} missing addresses to Supabase...")
    
    missing_data = [
        {"address": addr, "balance": local_holders[addr]}
        for addr in missing_addresses
    ]
    
    # Batch insert
    batch_size = 100
    synced = 0
    
    for i in range(0, len(missing_data), batch_size):
        batch = missing_data[i:i+batch_size]
        try:
            res = requests.post(
                f"{SB_URL}/rest/v1/holders",
                headers=headers,
                json=batch
            )
            if res.status_code in [200, 201, 204]:
                synced += len(batch)
                print(f"  [✓] Synced {synced}/{len(missing_data)}...", end="\r")
            else:
                print(f"\n  [!] Batch failed: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"\n  [!] Batch error: {e}")
    
    print(f"\n\n[✓] Successfully synced {synced} missing addresses!")
else:
    print(f"\n[✓] All addresses are already synced!")

print("\n" + "=" * 70)
print("SYNC COMPLETE!")
print("=" * 70)
