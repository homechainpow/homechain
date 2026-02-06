# 🚀 Quick Start Guide

Get up and running with $HOMEChain in less than 5 minutes.

## 1. Prerequisites
*   **Python 3.8+** installed.
*   **Git** installed.

## 2. Installation
Clone the repository:
```bash
git clone https://github.com/homechainpow/homechain.git
cd $HOMEchain
pip install -r requirements.txt
```

## 3. Create a Secure Wallet
**Do not skip this step.** You need a secure `.pem` file to store your mined coins.

```bash
python manage_wallet.py create
```
*   This creates `my_wallet.pem` (Your Private Key).
*   **BACKUP THIS FILE!** If you lose it, you strictly lose access to your funds.

## 4. Start Mining (Mainnet)
Connect to the Global Seed Node and start solving blocks.

```bash
python miner.py --node http://ec2-13-220-187-107.compute-1.amazonaws.com:5000 --wallet-file my_wallet.pem --threads 4
```

Replace `--threads 4` with the number of CPU cores you want to dedicate.

## 5. Check Your Stats
Go to the [Mainnet Explorer](http://ec2-13-220-187-107.compute-1.amazonaws.com:5000/dashboard/index.html) and check if your address appears in the "Live Blocks" list!
