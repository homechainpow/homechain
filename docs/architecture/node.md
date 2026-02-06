# The Node Structure

The $HOMEChain Node (`node.py`) is the backbone of the network. It performs three critical functions:
1.  **Validation**: Verifies every transaction and block against the consensus rules.
2.  **Storage**: Maintains the `chain_data.json` ledger.
3.  **Propagation**: Gossips data to other peers.

## Components

### 1. The Web Server (Aiohttp)
We use `aiohttp` to provide an asynchronous REST API. This ensures the node can handle thousands of requests (mining work, transactions) without blocking the main thread.

### 2. The Blockchain Manager
The `Blockchain` class (`blockchain.py`) wraps the list of blocks. It is responsible for:
*   `add_transaction()`: Adding to mempool.
*   `submit_block()`: Verifying PoW and appending to chain.
*   `save_chain()`: Persisting to disk.

### 3. The Wallet Manager
The `Wallet` class handles ECDSA (SECP256k1) key management. It ensures that only the owner of a private key can spend funds.
