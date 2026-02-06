# Mining Setup Guide

## Hardware Requirements
HomeChain is CPU-minable. You do not need a GPU.
*   **Minimum**: Raspberry Pi 4, 2GB RAM.
*   **Recommended**: ANY Laptop/Desktop (Intel/AMD), 4+ Cores.
*   **Ideal**: Dedicated VPS (4-8 vCPU).

## Step-by-Step

### 1. Get the Software
```bash
git clone https://github.com/homechainpow/homechain.git
cd $HOMEchain
pip install -r requirements.txt
```

### 2. Generate Your Vault (Wallet)
You need a place to put your coins.
```bash
python manage_wallet.py create
```
This generates `my_wallet.pem`. **Keep this safe.**

### 3. Run the Miner
```bash
python miner.py --node http://ec2-13-220-187-107.compute-1.amazonaws.com:5000 --wallet-file my_wallet.pem --threads 4
```

### 4. Monitor Progress
You will see output like:
```text
[Block #105] Mining with Diff 5...
Hashes: 450000...
💎 FOUND BLOCK! Nonce: 88123 Hash: 00000a7...
Submission: {"message": "Block Accepted"}
```
If you see "Block Accepted", congratulations! You just earned **132,575 $HOME**.
