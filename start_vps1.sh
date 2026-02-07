#!/bin/bash
SEED_IP="13.220.55.223"
MY_IP=$(curl -s ifconfig.me)
WALLET="7651ba54ae51a990abdefa0d7d0a4b86521bc7d973cb70a4ae4314b64b18f081"

echo "[*] Starting HomeChain Node on $MY_IP..."
cd /home/ubuntu/HomeChain
nohup python3 -u node.py --port 5005 > node.log 2>&1 &
sleep 5

echo "[*] Registering to Seed Node ($SEED_IP)..."
curl -X POST "http://$SEED_IP:5005/nodes/register" -H "Content-Type: application/json" -d "{\\"address\\": \\"http://$MY_IP:5005\\"}"

echo "[*] Starting Miner..."
nohup python3 -u miner.py --node http://localhost:5005 --address "$WALLET" > miner.log 2>&1 &

echo "[+] Node and Miner are up."
