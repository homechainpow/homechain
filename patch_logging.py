
import os

path = "/home/ubuntu/HomeChain/blockchain.py"
with open(path, "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "def add_transaction" in line:
        new_lines.append('        with open("/home/ubuntu/HomeChain/mempool.log", "a") as f: f.write(f"{time.time()}: add_transaction called\\n")\n')
    if "self.pending_transactions.append(transaction)" in line:
        new_lines.append('            with open("/home/ubuntu/HomeChain/mempool.log", "a") as f: f.write(f"{time.time()}: APPENDED. New size: {len(self.pending_transactions)}\\n")\n')
    if "def submit_block" in line:
        new_lines.append('        with open("/home/ubuntu/HomeChain/mempool.log", "a") as f: f.write(f"{time.time()}: submit_block called index={block_data.get(\'index\')}\\n")\n')
    if "self.pending_transactions = [" in line and "block_tx_signatures" in line:
        new_lines.append('        with open("/home/ubuntu/HomeChain/mempool.log", "a") as f: f.write(f"{time.time()}: mempool CLEANUP. signatures: {block_tx_signatures}\\n")\n')
        new_lines.append('        with open("/home/ubuntu/HomeChain/mempool.log", "a") as f: f.write(f"{time.time()}: mempool AFTER size: {len(self.pending_transactions)}\\n")\n')

with open(path, "w") as f:
    f.writelines(new_lines)
print("PATCH_COMPLETE")
