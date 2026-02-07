import sqlite3
import json

conn = sqlite3.connect('chain_v2.db')
c = conn.cursor()
target = "aa0ba2e22c9cd4a6bc50b5cb993a87ad9ff39e6c249460378799bb93216ed69d44a16d905db4b27c6305b19317420f4f2d6d66ab06e77b1ad5796646b212364c"
c.execute("SELECT idx FROM blocks WHERE data LIKE ?", (f'%{target}%',))
results = c.fetchall()
print(f"Blocks containing satya_main: {results}")

# Also check for part of it
partial = "4c6e77b1ad57"
c.execute("SELECT idx FROM blocks WHERE data LIKE ?", (f'%{partial}%',))
results_partial = c.fetchall()
print(f"Blocks containing 4c6e77b1ad57: {results_partial}")

conn.close()
