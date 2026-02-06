# $HOMEChain 🏠🔗 Roadmap

This document outlines the future development path for $HOMEChain.

## Phase 1-4: Core Foundation (Completed) ✅
- [x] **Layer 1 Protocol**: Python-based Blockchain (Block, Chain, Transaction).
- [x] **Consensus**: Proof of Work (SHA256-CPU) with Geometric Halving.
- [x] **Networking**: P2P Node REST API (Port 5000).
- [x] **Mining**: Multi-threaded CPU Miner with Secure Wallet support.
- [x] **Deployment**: Mainnet Live on AWS (Seed Node + High-Perf Miner).

## Phase 5: Usability & Security (Completed) ✅
- [x] **Secure Wallet**: `manage_wallet.py` (PEM Key Generation).
- [x] **Miner Security**: Updated Miner to read PEM files.

---

## Phase 6: Mobile & IoT (Next Steps) 🚧
*Goal: True Ubiquity - Mining on Fridge, Router, and Phone.*

- [ ] **Android App (APK)**: Convert `miner.py` into a native Python-for-Android service (Kivy/BeeWare) so it runs in background without Termux.
- [ ] **IoT Light Node**: Optimized version for Raspberry Pi Zero / ESP32.
- [ ] **QR Code Wallet**: Generate QR images for addresses to allow easy scanning.

## Phase 7: Ecosystem & DeFi 🚧
*Goal: Utility beyond holding.*

- [ ] **HomeNS (Name Service)**: Smart Contract to register `@satya` aliases for addresses.
- [ ] **Web Wallet**: Provide a web-interface for sending transactions (integrated into Dashboard).
- [ ] **Faucet**: Automatic free coin distribution for new users testnet.
- [ ] **DNS Seed**: Remove IP hardcoding; use DNS records to find peers automatically.

## Phase 8: Community Governance 🚧
- [ ] **DAO**: On-chain voting for protocol parameters (Block Size, Reward tweaks).
