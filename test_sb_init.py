import requests
import json

SB_URL = "https://hemzvtzsyybathuprizc.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlbXp2dHpzeXliYXRodXByaXpjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDQzMzg4NCwiZXhwIjoyMDg2MDA5ODg0fQ.xy8lenQXiE5Nv9AxI977zNhevXfZcvPgxO05XjQf0i8"

headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

def init_supabase():
    print("--- Initializing Supabase Tables ---")
    
    # Tables to create (using RPC or just direct SQL if possible, 
    # but since I don't have SQL endpoint via SDK easily, 
    # I'll check if tables exist by trying a select)
    
    tables = ["blocks", "transactions", "rewards", "stats", "holders"]
    
    for table in tables:
        url = f"{SB_URL}/rest/v1/{table}?limit=1"
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            print(f"[+] Table '{table}' exists.")
        else:
            print(f"[!] Table '{table}' missing or inaccessible: {res.status_code} - {res.text}")

    # Note: If tables are missing, I'd usually need to use the SQL Editor. 
    # But I will try to see if I can run the reset script logic.
    
if __name__ == "__main__":
    init_supabase()
