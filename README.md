# $HOMEChain 🏠🔗

**HomeChain** is a lightweight, Python-based Layer 1 blockchain designed to return crypto mining to the people. It runs on phones, laptops, and $HOME devices.

![HomeChain Status](https://img.shields.io/badge/Status-Mainnet_Live-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Consensus](https://img.shields.io/badge/Consensus-PoW_SHA256-orange)

## 🌟 Key Features

*   **O(1) Balances**: High-performance state database for instant lookups.
*   **Economic Security**: Mandatory 0.01 $HOME transaction fee to prevent spam.
*   **P2P Network**: Decentralized node discovery and mesh connectivity.
*   **Geometric Decay**: 50-Year Mining Schedule (Halves every era).

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
python miner.py --node http://13.220.55.223:5005 --wallet-file my_wallet.pem --threads 4
```

### 4. Run a Full Node (P2P)
Run your own node and connect to the global seed:
```bash
python node.py --port 5005
# Announce your node to the seed:
curl -X POST -H "Content-Type: application/json" -d '{"address": "http://YOUR_IP:5005"}' http://13.220.55.223:5005/nodes/register
```

## 📊 Explorer & Stats
View live blocks at the Official Scanner:
👉 **[https://homechain-scanner-55p3guxqp-yutupremsatus-projects.vercel.app/](https://homechain-scanner-55p3guxqp-yutupremsatus-projects.vercel.app/)**

Debug & Node Status:
👉 **[http://13.220.55.223:5005/debug/state](http://13.220.55.223:5005/debug/state)**

## 📜 Roadmap
Information on future updates (Mobile App, IoT) is in [ROADMAP.md](ROADMAP.md).

## ⚖️ License
This project is open-source under the **MIT License**.
