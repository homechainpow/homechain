import sqlite3
import json

conn = sqlite3.connect('chain_v2.db')
c = conn.cursor()
c.execute("SELECT idx, data FROM blocks ORDER BY idx ASC")
rows = c.fetchall()

addresses = set()
for idx, data_json in rows:
    try:
        data = json.loads(data_json)
        # Transactions
        for tx in data.get('transactions', []):
            addresses.add(tx.get('sender'))
            addresses.add(tx.get('receiver'))
        # Rewards
        for r in data.get('rewards', []):
            addresses.add(r.get('receiver'))
        # Validator
        addresses.add(data.get('validator'))
    except:
        pass

conn.close()

# Print any addresses that are not 128 chars but NOT None
print("--- Non-Standard Addresses in blocks ---")
for a in addresses:
    if a and len(str(a)) != 128:
        print(f"[{len(str(a))}] {a}")

print("\n--- Standard 128-char Addresses in blocks (Sample) ---")
count = 0
for a in addresses:
    if a and len(str(a)) == 128:
        print(a)
        count += 1
        if count >= 5: break
