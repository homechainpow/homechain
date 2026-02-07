import requests
import json

SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def fix_miners():
    miners = [
        {
            "address": "d0ea5e4d8f9c16e3ae9e4bbd574d96796646b212364c6e77b476e3390f000000",
            "wallet_name": "M2"
        },
        {
            "address": "0269989ba48c5938171d9d968556488a0e86a079237e174411f1852026000000",
            "wallet_name": "M3"
        }
    ]
    
    url = f"{SB_URL}/rest/v1/holders"
    res = requests.post(url, headers=headers, json=miners)
    if res.status_code in [200, 201, 204]:
        print("[+] Miners M2 and M3 successfully updated/upserted in Supabase.")
    else:
        print(f"[!] Critical Error: {res.text}")

if __name__ == "__main__":
    fix_miners()
