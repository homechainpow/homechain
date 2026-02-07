#!/bin/bash
# start_miner.sh
sudo pkill -9 -f miner.py
cd /home/ubuntu/HomeChain
echo "[*] Starting Miner at $(date)"
# Using the main Miner 1 wallet for rewards
nohup python3 -u miner.py --node http://localhost:5005 --address 7c2b0e66dceacc3c50410a2abb97a7067a43c231b897633458514930d4f07ba6 > miner.log 2>&1 &
echo "[*] Miner pushed to background."
sleep 5
tail -n 10 miner.log
