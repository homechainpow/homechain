# $HOMEChain 🏠🔗

**HomeChain** is a lightweight, Python-based Layer 1 blockchain designed to return crypto mining to the people. It runs on phones, laptops, and $HOME devices.

![HomeChain Status](https://img.shields.io/badge/Status-Mainnet_Live-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Consensus](https://img.shields.io/badge/Consensus-PoW_SHA256-orange)

## 🌟 Key Features

*   **100% Python**: Transparent, readable code. No binaries.
*   **One CPU, One Vote**: Optimized for general-purpose processors.
*   **Geometric Decay Sustainability**: 50-Year Mining Schedule (Halves every era).
*   **HomeNS**: Decentralized Naming Service (Coming Soon).

## 🚀 Quick Start (Mainnet)

### 1. Setup
```bash
git clone https://github.com/homechainpow/homechain.git
cd $HOMEchain
pip install -r requirements.txt
```

### 2. Create Wallet (Secure)
**Do not use manual addresses!** Create a secure keypair:
```bash
python manage_wallet.py create
# Saves 'my_wallet.pem' - KEEP THIS SAFE!
```

### 3. Start Mining
Join the global mesh network:
```bash
python miner.py --node http://ec2-13-220-187-107.compute-1.amazonaws.com:5000 --wallet-file my_wallet.pem --threads 4
```

## 📊 Explorer & Stats
View live blocks at the Seed Node Dashboard:
👉 **[http://ec2-13-220-187-107.compute-1.amazonaws.com:5000/dashboard/index.html](http://ec2-13-220-187-107.compute-1.amazonaws.com:5000/dashboard/index.html)**

## 📜 Roadmap
Information on future updates (Mobile App, IoT) is in [ROADMAP.md](ROADMAP.md).

## ⚖️ License
This project is open-source under the **MIT License**.
