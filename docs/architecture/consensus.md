# Consensus Mechanism: Proof of Work

HomeChain uses a custom implementation of **Proof of Work (PoW)**, similar to Bitcoin but tuned for consumer hardware.

## The Algorithm: SHA256-CPU
We utilize a single-pass `SHA-256` hashing algorithm. Unlike Bitcoin's `SHA-256d` (Double SHA), our single-pass approach reduces the overhead for low-power devices while maintaining cryptographic security.

### Difficulty Adjustment
To ensure reliable block times of **60 seconds**, the network adjusts difficulty after every block.

*   **Target Block Time**: 60 Seconds.
*   **Mechanism**: The `difficulty` parameter (number of leading zeros required) is dynamic.
*   **Anti-Instamine**: If blocks are found too fast (< 10s), difficulty increases immediately.

## Why PoW?
In an era of Proof of Stake (PoS), why chose PoW?
1.  **Fair Distribution**: Coins are minted by *work*, not by pre-existing wealth.
2.  **Physical Security**: Attacking the network requires real-world energy and hardware, making it costly to spam or rewrite history.
3.  **Simplicity**: PoW is the most battle-tested consensus model in history.
