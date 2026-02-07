import requests
import re
import json

# Supabase Config
with open('C:/Users/Administrator/.gemini/antigravity/scratch/HomeChain/supabase_sync.py', 'r') as f:
    content = f.read()
    sb_url = re.search(r'SB_URL = "(.*?)"', content).group(1)
    sb_key = re.search(r'SB_KEY = "(.*?)"', content).group(1)

headers = {
    "apikey": sb_key,
    "Authorization": f"Bearer {sb_key}"
}

def deep_audit_production():
    print("=== Production Content Audit ===")
    
    # 1. Check Holders
    h_res = requests.get(f"{sb_url}/rest/v1/holders", headers=headers)
    holders = h_res.json() if h_res.status_code == 200 else []
    
    invalid_holders = []
    for h in holders:
        addr = h['address']
        if len(addr) != 128 or not all(c in '0123456789abcdefABCDEF' for c in addr):
            invalid_holders.append(h)
            
    print(f"Total Holders: {len(holders)}")
    print(f"Invalid Holders: {len(invalid_holders)}")
    for ih in invalid_holders[:5]:
        print(f"  [!] {ih['address']}")

    # 2. Check Blocks (Gaps)
    b_res = requests.get(f"{sb_url}/rest/v1/blocks?select=id&order=id.asc", headers=headers)
    blocks = b_res.json() if b_res.status_code == 200 else []
    block_ids = [b['id'] for b in blocks]
    
    gaps = []
    if block_ids:
        for i in range(max(block_ids)):
            if i not in block_ids:
                gaps.append(i)
    
    print(f"Total Blocks: {len(blocks)}")
    print(f"Height Gaps: {len(gaps)}")
    if gaps:
        print(f"  First Gaps: {gaps[:10]}")

    # 3. Check Transactions (Address Format)
    t_res = requests.get(f"{sb_url}/rest/v1/transactions?limit=1000", headers=headers)
    txs = t_res.json() if t_res.status_code == 200 else []
    
    invalid_tx_addrs = 0
    for t in txs:
        s, r = t.get('sender', ''), t.get('receiver', '')
        if (len(s) != 128 and s != 'SYSTEM' and s != 'GENESIS') or (len(r) != 128 and r != 'SYSTEM' and r != 'GENESIS'):
            invalid_tx_addrs += 1
            if invalid_tx_addrs < 3:
                print(f"  [!] Invalid TX addr found in Block #{t['block_id']}: {s[:16]}... -> {r[:16]}...")

    print(f"Sample TX Address Check (1000 txs): {invalid_tx_addrs} issues found.")

if __name__ == "__main__":
    deep_audit_production()
