# API Reference

The $HOMEChain Node exposes a simple REST API on port `5000` by default.

## Base URL
`http://<node-ip>:5000`

## Endpoints

### 1. Get Blockchain Data
**GET** `/chain`
Returns the full blockchain and supply stats.
```json
{
  "length": 105,
  "chain": [...],
  "supply": 15000000,
  "max_supply": 21000000000
}
```

### 2. Get Mining Work
**GET** `/mining/get-work?address=<YOUR_ADDRESS>`
Returns the template for the next block to be mined.
*   `address` (Required): The wallet address to receive rewards.

### 3. Submit Block
**POST** `/mining/submit`
Submit a solved block candidate.
*   **Body**: JSON object containing the block data + `nonce`.

### 4. Get Balance
**GET** `/balance/<address>`
Returns the balance of a specific address.

### 5. Send Transaction
**POST** `/transactions/new`
Broadcast a new transaction to the network.
*   **Body**:
    ```json
    {
        "sender": "0x...",
        "receiver": "0x...",
        "amount": 100,
        "signature": "..."
    }
    ```
