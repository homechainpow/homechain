#!/bin/bash
echo "[*] Cleaning up old data..."
sudo pkill -9 -f node.py
sudo pkill -9 -f miner.py
sudo pkill -9 -f supabase_sync.py
rm -rf /home/ubuntu/HomeChain
mkdir -p /home/ubuntu/HomeChain

echo "[*] Ready for code deployment."
