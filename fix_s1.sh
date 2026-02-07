#!/bin/bash
# Force restart node on S1
pkill -9 -f node.py
sleep 2
cd HomeChain
nohup python3 node.py -p 5005 > node.log 2>&1 &
sleep 3
echo "=== S1 Node Status ==="
curl -s http://localhost:5005/debug/state || echo "Node not responding"
