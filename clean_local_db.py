import sqlite3

# Clean up invalid addresses from local DB
conn = sqlite3.connect('chain_v2.db')
c = conn.cursor()

# Get all invalid addresses (not 128 chars or not hex)
c.execute("SELECT address FROM balances WHERE length(address) != 128")
invalid_addresses = [row[0] for row in c.fetchall()]

print(f"Found {len(invalid_addresses)} invalid addresses in local DB")
print(f"Deleting: {invalid_addresses[:10]}...")

if invalid_addresses:
    for addr in invalid_addresses:
        c.execute("DELETE FROM balances WHERE address = ?", (addr,))
    conn.commit()
    print(f"\n[✓] Deleted {len(invalid_addresses)} invalid addresses from local DB")
else:
    print("\n[✓] No invalid addresses found")

# Verify
c.execute("SELECT COUNT(*) FROM balances")
remaining = c.fetchone()[0]
print(f"\n[✓] Remaining valid addresses: {remaining}")

conn.close()
