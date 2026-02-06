#!/bin/bash
START=1
END=300
NODE="http://localhost:5005"
THROTTLE=5.0
WALLET_DIR="wallets_300"

echo "🚀 Launching 300 miners from $WALLET_DIR..."
ulimit -n 65535
mkdir -p logs_300

for (( i=$START; i<=$END; i++ ))
do
    WALLET="${WALLET_DIR}/p${i}.pem"
    # Using nohup and disowning to keep it alive
    nohup python3 miner.py --wallet-file $WALLET --node $NODE --throttle $THROTTLE --device-id "HC_SWARM_${i}" > logs_300/miner_${i}.log 2>&1 &
    
    if (( $i % 50 == 0 )); then
        echo "✅ Started $i miners..."
        sleep 1
    fi
done
echo "🎉 300 Miners Swarm Launched!"
