# Architecture Overview

HomeChain follows a **Modular Monolithic** architecture pattern. It is designed to be lightweight, easy to maintain, and performant on low-end hardware.

## High-Level Components

The system is composed of four main layers:

1.  **Network Layer (`node.py`)**: Handles P2P communication, block propagation, and transaction gossiping.
2.  **Consensus Layer (`consensus.py`)**: Implements the Proof of Work (PoW) algorithm to secure the global state.
3.  **State Layer (`blockchain.py`)**: Manages the ledger, block storage (`chain_data.json`), and validity rules.
4.  **Application Layer (`vm.py`)**: A lightweight Virtual Machine for executing simple smart contracts and specialized transaction types (like $HOMENS).

## Data Flow

When a user submits a transaction:
1.  **Node** receives it via API (`/transactions/new`).
2.  **Blockchain** validates signatures and balances.
3.  **Mempool** stores the valid pending transaction.
4.  **Miners** pick up the transaction, solve the PoW puzzle.
5.  **Network** propagates the new block.
6.  **State** is updated globally.
