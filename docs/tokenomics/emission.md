# Geometric Emission Schedule

HomeChain uses a unique **Geometric Decay** model for its emission, distinct from the step-function halvings of Bitcoin.

## The Problem with Traditional Halving
Bitcoin halves rewards every 4 years. This creates a "Cliff":
1.  Miners suddenly lose 50% of revenue overnight.
2.  Network security can drop sharpely.
3.  Fees must skyrocket to compensate.

## The $HOMEChain Solution
We smooth this curve using shorter "Eras".

### The Formula
The reward halves every Era, but the *length* of the Era doubles.

> **Era 1**: 10 Days -> High Reward
> **Era 2**: 20 Days -> Medium Reward
> **Era 3**: 40 Days -> Lower Reward

This ensures a **Logarithmic** distribution of coins over 50 years, keeping mining profitable for a lifetime, not just the first 4 years.
