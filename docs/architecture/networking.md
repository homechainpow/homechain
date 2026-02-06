# Networking Protocol

HomeChain uses a simple P2P mesh network over HTTP.

## Peer Discovery
*   **Seed Nodes**: Ideally, hardcoded DNS seeds or IP addresses in `node.py`.
*   **Gossip**: When a node connects to a peer, it can ask for *that* peer's list of neighbors.

## Protocol Messages

### 1. New Block
When a miner finds a block, it POSTs it to:
`POST /mining/submit`

### 2. New Transaction
When a user sends money, the transaction is broadcast to:
`POST /transactions/new`

## Future Improvements
*   **Kademlia DHT**: For decentralized peer discovery without seed nodes.
*   **TCP/Socket**: Replacing HTTP with persistent TCP sockets to reduce latency.
