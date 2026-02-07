#!/bin/bash
SEED_IP="13.220.55.223"
MY_IP=$(curl -s ifconfig.me)
WALLET="8c0829602c7bbbbf6612a284e8f47c87023363364f9f25793e1107563c6b6534"

echo "[*] Starting HomeChain Node on $MY_IP..."
cd /home/ubuntu/HomeChain
nohup python3 -u node.py --port 5005 > node.log 2>&1 &
sleep 5

echo "[*] Registering to Seed Node ($SEED_IP)..."
curl -X POST "http://$SEED_IP:5005/nodes/register" -H "Content-Type: application/json" -d "{\\"address\\": \\"http://$MY_IP:5005\\"}"

echo "[*] Starting Miner..."
nohup python3 -u miner.py --node http://localhost:5005 --address "$WALLET" > miner.log 2>&1 &

echo "[+] Node and Miner are up."
