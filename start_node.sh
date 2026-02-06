#!/bin/bash
# 1. Kill cleanup
# Only kill relevant processes
sudo pkill -f python3
sudo pkill -f lt

cd /home/ubuntu/homechain

# 2. Start API Node
nohup python3 node.py > node.log 2>&1 &
echo "API Node Started"
sleep 5

# 3. Start Miner (using VPS Wallet)
if [ ! -f "wallets/vps_wallet.pem" ]; then
    python3 manage_wallet.py generate wallets/vps_wallet.pem
fi
nohup python3 miner.py --node http://127.0.0.1:5000 --wallet wallets/vps_wallet.pem > miner.log 2>&1 &
echo "Miner Started"

# 4. Start Localtunnel with UNIQUE subdomain
# Using nohup to keep it running
nohup lt --port 5000 --local-host 127.0.0.1 --subdomain homechain-mainnet-x82z > tunnel.log 2>&1 &

echo "System Fully Operational: https://homechain-mainnet-x82z.loca.lt"
