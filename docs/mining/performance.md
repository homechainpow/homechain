# Mining Performance Tuning

Maximizing your hashrate on $HOMEChain.

## CPU Mining Fundamentals
HomeChain uses SHA256-CPU. This algorithm is computationally intensive but benefits from:
1.  **High Clock Speed**: Faster GHz = Faster Hashing.
2.  **Number of Cores**: More cores = Linearly more rewards.

## Optimization Tips

### 1. Thread Count
Use the `--threads` flag.
*   Default: 1 Thread.
*   **Recommended**: `Total Cores - 1` (Leave one core for OS tasks).
    ```bash
    python miner.py --threads 7
    ```

### 2. Background Processes
Close Chrome, Games, and other heavy apps. Mining requires dedicated CPU time.

### 3. Cooling
Mining pushes your CPU to 100%. Ensure your fans are working! Thermal throttling will reduce your hashrate by 50% or more.
