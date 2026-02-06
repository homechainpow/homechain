import requests
try:
    print("Testing connection to http://localhost:5000/chain (Tunneled to VPS)...")
    r = requests.get("http://localhost:5000/chain")
    if r.status_code == 200:
        data = r.json()
        chain = data.get('chain', [])
        print(f"✅ SUCCESS! Connected to HomeChain Node.")
        print(f"📦 Block Height: {len(chain)}")
        print(f"💰 First Block Valid: {chain[0]['validator'] == 'SYSTEM'}")
        print(f"🔗 Last Hash: {chain[-1]['hash'][:10]}...")
    else:
        print(f"❌ Error: Status Code {r.status_code}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
