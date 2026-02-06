#!/bin/bash
# start_node.sh
sudo pkill -9 -f node.py
cd /home/ubuntu/HomeChain
echo "[*] Starting Node at $(date)"
nohup python3 -u node.py --port 5005 > node.log 2>&1 &
echo "[*] Node pushed to background. Waiting for initialization..."
sleep 15
tail -n 10 node.log
