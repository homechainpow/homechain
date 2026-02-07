import requests
import json

# Configuration
SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def cleanup_holders():
    print("🧹 Cleaning up invalid holders...")
    
    # List of invalid or placeholder names seen in the screenshot
    invalid_addresses = ["GENESIS", "SYSTEM", "M1"]
    
    # We also want to delete anything that isn't a long hex string (usually 128 chars for our keys)
    # But to be safe, we'll start with the specific ones and those clearly too short to be public keys.
    
    for addr in invalid_addresses:
        url = f"{SB_URL}/rest/v1/holders?address=eq.{addr}"
        res = requests.delete(url, headers=headers)
        if res.status_code in [200, 201, 204]:
            print(f"  ✅ Deleted: {addr}")
        else:
            print(f"  ❌ Failed to delete {addr}: {res.status_code}")

    # Delete 'S_901' etc.
    # We can use a pattern match if supported, or just fetch and delete.
    url = f"{SB_URL}/rest/v1/holders?address=like.S_*"
    res = requests.delete(url, headers=headers)
    if res.status_code in [200, 201, 204]:
        print(f"  ✅ Deleted pattern S_*")
    
    print("\n✨ Cleanup Complete!")

if __name__ == "__main__":
    cleanup_holders()
