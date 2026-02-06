# Running a Full Node

Running a node strengthens the network.

## why Run a Node?
*   **Security**: Verify your own transactions. Don't trust others.
*   **Privacy**: Don't leak your IP/Transactions to public nodes.
*   **Support**: Help the network survive.

## Setup Guide

### 1. Server Requirements
*   **OS**: Ubuntu 20.04+ (Recommended) or Windows.
*   **Port 5000**: Must be open (TCP).

### 2. Commands
```bash
# Clone
git clone https://github.com/homechainpow/homechain.git
cd $HOMEchain

# Dependencies
pip3 install -r requirements.txt

# Run (Background)
nohup python3 node.py > node.log 2>&1 &
```

### 3. Verify
Check if it's syncing:
```bash
curl http://localhost:5000/chain
```
