import sqlite3
import json

conn = sqlite3.connect('chain_v2.db')
c = conn.cursor()
c.execute("SELECT idx, data FROM blocks ORDER BY idx ASC")
rows = c.fetchall()

total_rewards = 0
total_tx_amount = 0
holder_rewards = {}

for idx, data_json in rows:
    data = json.loads(data_json)
    # Summ rewards
    block_reward = 0
    for r in data.get('rewards', []):
        amt = int(r.get('amount', 0))
        addr = r.get('receiver')
        block_reward += amt
        holder_rewards[addr] = holder_rewards.get(addr, 0) + amt
    
    total_rewards += block_reward
    
    # Sum transactions
    for tx in data.get('transactions', []):
        total_tx_amount += int(tx.get('amount', 0))

conn.close()

print(f"Blocks processed: {len(rows)}")
print(f"Total Rewards (from JSON): {total_rewards/100000000:.2f} HOME")
print(f"Total TX Volume: {total_tx_amount/100000000:.2f} HOME")
print(f"Unique Reward Recipients: {len(holder_rewards)}")

# Top 5 reward recipients
sorted_rewards = sorted(holder_rewards.items(), key=lambda x: x[1], reverse=True)
print("\nTop 5 Reward Recipients:")
for addr, amt in sorted_rewards[:5]:
    print(f"  {addr[:16]}... : {amt/100000000:.2f} HOME")
