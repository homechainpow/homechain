# Wallet Management

HomeChain uses **SECP256k1** elliptic curve cryptography (same as Bitcoin/Ethereum) to secure funds.

## Wallet File Format (`.pem`)
We store private keys in the standard PEM format. This allows for easy interoperability and security.

**Example `my_wallet.pem`:**
```text
-----BEGIN EC PRIVATE KEY-----
MHQCAQEEI...
...
-----END EC PRIVATE KEY-----
```

## Creating a Wallet
Use the built-in tool:
```bash
python manage_wallet.py create
```

## Improving Security
1.  **Cold Storage**: Move your `.pem` file to a USB drive and delete it from your mining PC.
2.  **Backups**: Make 2-3 copies of your key.
3.  **Never Share**: Your private key GIVES ACCESS to your funds. Never send the `.pem` file to anyone.
