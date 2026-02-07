import requests
import json

# Configuration
SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlmXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

def purge_supabase():
    print("🧹 Purging invalid data from Supabase...")
    
    # 1. Purge S_ labels
    url = f"{SB_URL}/rest/v1/holders?address=like.S_*"
    res = requests.delete(url, headers=headers)
    print(f"  [+] Purge S_ labels: {res.status_code}")
    
    # 2. Purge Truncated Addresses (e.g. length 89)
    # We can fetch and delete specific ones we know.
    truncated = [
        "aa0ba2e22c9cd4a6bc50b5c18bab9685ed69f9876e6b093390c7511d433644d96796646b212364c6e77b1ad57"
    ]
    for addr in truncated:
        url = f"{SB_URL}/rest/v1/holders?address=eq.{addr}"
        res = requests.delete(url, headers=headers)
        print(f"  [+] Purge Truncated {addr[:8]}: {res.status_code}")

    # 3. Purge Literal Labels
    literals = ["SYSTEM", "GENESIS", "M1", "M2", "M3"]
    for addr in literals:
        url = f"{SB_URL}/rest/v1/holders?address=eq.{addr}"
        res = requests.delete(url, headers=headers)
        print(f"  [+] Purge Literal {addr}: {res.status_code}")

    print("✨ Purge Complete.")

if __name__ == "__main__":
    purge_supabase()
