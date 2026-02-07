#!/bin/bash
pkill -f node.py
cd HomeChain
nohup python3 node.py -p 5005 > node.log 2>&1 &
sleep 2
echo "Node restarted successfully"
