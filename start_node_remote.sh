#!/bin/bash
SEED_IP="13.220.55.223"
MY_IP=$(curl -s ifconfig.me)

echo "[*] Starting HomeChain Node on $MY_IP..."
cd /home/ubuntu/HomeChain
nohup python3 -u node.py --port 5005 > node.log 2>&1 &
sleep 3

echo "[*] Registering to Seed Node ($SEED_IP)..."
curl -X POST "http://$SEED_IP:5005/nodes/register" -H "Content-Type: application/json" -d "{\"address\": \"http://$MY_IP:5005\"}"

echo "[*] Starting Miner..."
# Using some random addresses for diversity
WALLET="vps_$(hostname)"
nohup python3 -u miner.py --node http://localhost:5005 --address "$WALLET" > miner.log 2>&1 &

echo "[+] Node and Miner are up."
