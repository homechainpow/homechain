# $HOMEChain Mining Guide ⛏️

This guide explains how to run a local miner on your machine.

## Prerequisites
Ensure strict adherence to the [security protocol](docs/mining/wallet.md) by generating a secure wallet before proceeding.

### 1. Start the Node (Ledger)
This terminal acts as your local gateway to the blockchain network. Keep this window open.
```powershell
cd $HOMEChain
python node.py
```

### 2. Start the Miner (Worker)
Open a **second terminal**. This process will utilize your CPU to validate blocks.
Make sure to reference your secure wallet file.

```powershell
cd $HOMEChain
python miner.py --wallet-file wallets/my_wallet.pem --threads 4
```

> **Performance Optimization:**
> - Use `--threads <N>` where N is your CPU core count minus one.
> - To mine on a remote node, use `--node http://<IP>:5000`.
