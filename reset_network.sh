
#!/bin/bash
echo "[*] Killing all HomeChain processes..."
sudo pkill -9 -f node.py
sudo pkill -9 -f miner.py
sudo pkill -9 -f supabase_sync.py
sudo pkill -9 -f bot.py

echo "[*] Cleaning up logs..."
rm /home/ubuntu/HomeChain/*.log

echo "[*] Restarting Node..."
cd /home/ubuntu/HomeChain
nohup python3 -u node.py --port 5005 > node.log 2>&1 &
sleep 5

echo "[*] Restarting Miners..."
nohup python3 -u miner.py --node http://localhost:5005 --address 7c2b0e66dceacc3c50410a2abb97a7067a43c231b897633458514930d4f07ba6 > miner.log 2>&1 &

echo "[*] Restarting Stress Bot..."
nohup python3 -u stress_test_bot.py > bot.log 2>&1 &

echo "[*] Wiping Supabase (External)..."
# I will do this from the local machine since I have the script there.

echo "[*] Restarting Sync..."
nohup python3 -u supabase_sync.py > sync.log 2>&1 &

echo "[+] Done."
