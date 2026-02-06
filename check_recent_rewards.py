
import sqlite3
import json

db_path = "/home/ubuntu/HomeChain/chain_v2.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT idx, data FROM blocks ORDER BY idx DESC LIMIT 15")
rows = c.fetchall()

print("LATEST BLOCK WINNERS (Top 15):")
for idx, data_json in rows:
    data = json.loads(data_json)
    validator = data.get('validator', 'UNKNOWN')
    timestamp = data.get('timestamp')
    print(f"Block #{idx} | Winner: {validator}")
