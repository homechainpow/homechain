from wallet import Wallet
import os
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
print("SYNC ALL WALLETS FROM FOLDER TO SUPABASE")
print("=" * 70)

# 1. Load all wallet addresses from PEM files
wallet_dir = "wallets"
pem_files = [f for f in os.listdir(wallet_dir) if f.endswith('.pem')]
print(f"\n[*] Found {len(pem_files)} PEM files in wallets folder")

wallet_addresses = {}
for pem_file in pem_files:
    try:
        w = Wallet.load_from_pem(os.path.join(wallet_dir, pem_file))
        wallet_addresses[w.address] = pem_file
    except Exception as e:
        print(f"[!] Failed to load {pem_file}: {e}")

print(f"[✓] Loaded {len(wallet_addresses)} wallet addresses")

# 2. Get balances from local DB
conn = sqlite3.connect('chain_v2.db')
c = conn.cursor()

wallet_balances = {}
missing_from_db = []

for addr, pem_name in wallet_addresses.items():
    c.execute("SELECT balance FROM balances WHERE address = ?", (addr,))
    result = c.fetchone()
    if result:
        wallet_balances[addr] = int(result[0])
    else:
        missing_from_db.append((addr, pem_name))

conn.close()

print(f"\n[LOCAL DB]")
print(f"  Wallets with balance: {len(wallet_balances)}")
print(f"  Wallets missing: {len(missing_from_db)}")
print(f"  Total supply: {sum(wallet_balances.values())/100000000:.2f} HOME")

if missing_from_db:
    print(f"\n[!] Missing from DB:")
    for addr, pem in missing_from_db[:10]:
        print(f"    {pem}: {addr[:16]}...")

# 3. Get current Supabase holders
try:
    res = requests.get(f"{SB_URL}/rest/v1/holders?select=address", headers=headers)
    sb_addresses = set(h['address'] for h in res.json())
    print(f"\n[SUPABASE]")
    print(f"  Current holders: {len(sb_addresses)}")
except Exception as e:
    print(f"\n[!] Error fetching Supabase: {e}")
    sb_addresses = set()

# 4. Find wallets to sync
to_sync = []
for addr, balance in wallet_balances.items():
    if addr not in sb_addresses:
        to_sync.append({"address": addr, "balance": balance})

print(f"\n[TO SYNC]")
print(f"  Wallets to add: {len(to_sync)}")
print(f"  Supply to add: {sum(w['balance'] for w in to_sync)/100000000:.2f} HOME")

# 5. Sync to Supabase
if to_sync:
    print(f"\n[*] Syncing {len(to_sync)} wallets to Supabase...")
    
    batch_size = 100
    synced = 0
    
    for i in range(0, len(to_sync), batch_size):
        batch = to_sync[i:i+batch_size]
        try:
            res = requests.post(
                f"{SB_URL}/rest/v1/holders",
                headers=headers,
                json=batch
            )
            if res.status_code in [200, 201, 204]:
                synced += len(batch)
                print(f"  [✓] Synced {synced}/{len(to_sync)}...", end="\r")
            else:
                print(f"\n  [!] Batch failed: {res.status_code}")
        except Exception as e:
            print(f"\n  [!] Batch error: {e}")
    
    print(f"\n\n[✓] Successfully synced {synced} wallets!")
else:
    print(f"\n[✓] All wallets already synced!")

# 6. Final verification
try:
    res = requests.get(f"{SB_URL}/rest/v1/holders?select=balance", headers=headers)
    total_supply = sum(h['balance'] for h in res.json())
    count = len(res.json())
    print(f"\n[FINAL STATUS]")
    print(f"  Total holders in Supabase: {count}")
    print(f"  Total supply in Supabase: {total_supply/100000000:.2f} HOME")
except:
    pass

print("\n" + "=" * 70)
print("SYNC COMPLETE!")
print("=" * 70)
