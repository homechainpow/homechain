import subprocess
import os
import time

def launch_swarm(count=200):
    print(f"🚀 Launching {count} Miners...")
    node_url = "http://localhost:5005"
    wallet_dir = "wallets"
    
    # Get list of wallet files
    wallets = sorted([f for f in os.listdir(wallet_dir) if f.endswith(".pem")])
    
    if len(wallets) < count:
        print(f"Warning: Only found {len(wallets)} wallets. Launching all available.")
        count = len(wallets)

    processes = []
    
    for i in range(count):
        wallet_path = os.path.join(wallet_dir, wallets[i])
        device_id = f"HP_ANDROID_SIM_{i:03}" # Generating unique device IDs for Anti-Sybil
        
        # Command: python3 miner.py --node http://localhost:5000 --wallet-file wallets/p1.pem --throttle 0.5
        cmd = [
            "python3", "miner.py",
            "--node", node_url,
            "--wallet-file", wallet_path,
            "--throttle", "0.2" # Add some throttle to not burn the CPU
        ]
        
        # We also need to pass device_id. Let's modify miner.py locally first or pass via env.
        # Actually, let's update miner.py to accept --device-id.
        
        log_file = open(f"logs/miner_{i}.log", "w")
        p = subprocess.Popen(cmd, stdout=log_file, stderr=log_file)
        processes.append(p)
        
        if i % 10 == 0:
            print(f"Started {i} miners...")
            time.sleep(1) # Stagger starts

    print(f"✅ Successfully launched {len(processes)} miners.")
    return processes

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10, help="Number of miners to launch")
    args = parser.parse_args()
    
    if not os.path.exists("logs"): os.makedirs("logs")
    launch_swarm(args.count)
