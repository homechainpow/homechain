# HomeChain Core V2 (Stable 2.11) 🏙️💎🚀

## Overview
HomeChain V2 is a high-performance PoW blockchain with SQLite-based state persistence and PPLNS reward models. This version introduces the **Blockchain-Authoritative Sync** methodology for 100% data accuracy.

## Key Methodologies
### 1. Blockchain-Authoritative Sync
To ensure the scanner and wallets always reflect the truth, we use a "Replay-from-Genesis" strategy:
- **Authoritative Source**: The raw block data is the ONLY source of truth.
- **State Replay**: Balances are calculated by replaying transactions/rewards from Block #0.
- **Label Resolution**: Legacy labels (e.g., S_994) are mapped to 128-char HEX addresses using PEM-derived manifests during the replay process.

### 2. Database Engine
- **Engine**: SQLite (via `chain_v2.db`).
- **Persistence**: Transactions, rewards, and difficulty adjustments are atomically stored.
- **Pruning**: Support for block pruning to maintain mobile node efficiency.

## Security Features
- **SMA Difficulty**: 144-block window for smooth hashpower adjustments.
- **MTP Protection**: Timestamp manipulation prevention.
- **Merkle Roots**: Cryptographic integrity for transaction sets.

## Repository Structure
- `node.py`: Core blockchain node.
- `consensus.py`: PoW and state transition logic.
- `supabase_sync.py`: Live production sync worker.

---
*Stable Release: 2.11 (February 2026)*
🏙️💎🌍🚀
