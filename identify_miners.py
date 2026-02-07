from wallet import Wallet
import os

keys = {
    'S1 (xelis1.pem)': 'C:/D/xelis1.pem',
    'S2 (arduino1.pem)': 'C:/D/arduino1.pem',
    'S3 (miner.pem)': 'C:/D/miner.pem'
}

print("=== Miner Address Identification ===")
for name, path in keys.items():
    if os.path.exists(path):
        try:
            w = Wallet.load_from_pem(path)
            print(f"{name}: {w.address}")
        except Exception as e:
            print(f"{name}: Failed to load ({e})")
    else:
        print(f"{name}: Not found at {path}")

# Also check wallets folder for miner equivalents
wallet_dir = 'wallets'
if os.path.exists(wallet_dir):
    print("\n=== Wallets Folder Scan ===")
    for f in os.listdir(wallet_dir):
        if 'miner' in f.lower() or 'vps' in f.lower():
            try:
                w = Wallet.load_from_pem(os.path.join(wallet_dir, f))
                print(f"{f}: {w.address}")
            except:
                pass
