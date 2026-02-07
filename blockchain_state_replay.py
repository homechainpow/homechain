import sqlite3
import json
import re
import os

# --- SETTINGS ---
DB_PATH = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/chain_v2.db'
MANIFEST_PATH = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/MASTER_WALLETS_MANIFEST.json'
OUTPUT_STATE = 'C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/REPLAYED_STATE.json'

def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        print(f"Warning: Manifest not found at {MANIFEST_PATH}")
        return {}
    with open(MANIFEST_PATH, 'r') as f:
        return json.load(f)

def replay_blockchain():
    print("=== Blockchain State Replay (Authoritative) ===")
    
    manifest = load_manifest()
    # Normalize manifest: S_944 -> hex
    # But wait, the manifest is HEX -> FILENAMES. We need LABEL -> HEX.
    # Actually, the user wants us to know that S_xxx labels correspond to p1, p2 etc.
    # Let's build a quick mapping for the known S-labels.
    label_to_hex = {}
    for hex_addr, files in manifest.items():
        for f_info in files:
            # Extract label like 'p10' from 'p10.pem (from wallets)'
            match = re.search(r'(p\d+)\.pem', f_info)
            if match:
                p_label = match.group(1) # e.g. 'p10'
                # Convert p10 to S_910 style? No, let's keep it simple.
                # In the chain, labels are S_901 to S_1000 and S_1101 to S_1181
                # p1..p100 -> S_901..S_1000
                # p201..p281 -> S_1101..S_1181
                p_num = int(p_label[1:])
                if 1 <= p_num <= 100:
                    s_label = f"S_{900 + p_num}"
                    label_to_hex[s_label] = hex_addr
                elif 201 <= p_num <= 281:
                    s_label = f"S_{900 + p_num}" # S_1101 is 900 + 201 = 1101. Correct.
                    label_to_hex[s_label] = hex_addr

    balances = {} # addr -> balance

    def add_balance(addr, amount):
        # Resolve address mapping
        clean_addr = label_to_hex.get(addr, addr)
        # If still not valid hex (and not system), warn
        if len(clean_addr) != 128 and clean_addr not in ['SYSTEM', 'GENESIS']:
            # We skip system labels for the "holders" list later, but track them for replay logic
            pass
        
        balances[clean_addr] = balances.get(clean_addr, 0) + amount

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT idx, data FROM blocks ORDER BY idx ASC")
    
    total_blocks = 0
    for idx, data_json in c.fetchall():
        block_data = json.loads(data_json)
        
        # 1. Process Rewards
        for rew in block_data.get('rewards', []):
            add_balance(rew['receiver'], int(rew['amount']))
            
        # 2. Process Transactions
        for tx in block_data.get('transactions', []):
            sender = tx['sender']
            receiver = tx['receiver']
            amount = int(tx['amount'])
            fee = int(tx.get('fee', 1000000))
            
            add_balance(sender, -(amount + fee))
            add_balance(receiver, amount)
            # Fee goes to validator (usually via reward in next block or handled in consensus)
            # In our current simplistic V2 data model, fees are effectively burned or 
            # captured in the reward distributions if explicitly listed.
            # If not explicitly reward-distributed, we treat them as subtracted from sender.

        total_blocks = idx

    print(f"[✓] Replayed to Block #{total_blocks}")
    
    # Filter out 0 balances and system labels for the final holders report
    final_holders = {addr: bal for addr, bal in balances.items() 
                     if bal > 0 and len(addr) == 128}

    print(f"    Calculated {len(final_holders)} valid HEX holders.")
    print(f"    Total Supply in HEX wallets: {sum(final_holders.values())/10**8:.2f} HOME")

    with open(OUTPUT_STATE, 'w') as f:
        json.dump(final_holders, f, indent=4)
        
    print(f"[*] Replayed state saved to {OUTPUT_STATE}")
    conn.close()

if __name__ == "__main__":
    replay_blockchain()
