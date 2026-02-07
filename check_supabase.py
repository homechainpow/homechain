import json
from supabase import create_client, Client
import os

# Load config from scanner lib if possible, or use defaults from previous turns
SUPABASE_URL = "https://oxzlkfzqxfzqwfzqxfzq.supabase.co" # Placeholder, I should get real one
SUPABASE_KEY = "eyJhbG..." # Placeholder

# Let's try to find the real credentials in the scanner folder
SCRATCH_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch"
SCANNER_LIB = os.path.join(SCRATCH_DIR, "homechain-scanner", "src", "lib", "supabase.ts")

def get_creds():
    try:
        with open(SCANNER_LIB, 'r') as f:
            content = f.read()
            url = content.split('NEXT_PUBLIC_SUPABASE_URL || "')[1].split('"')[0]
            key = content.split('NEXT_PUBLIC_SUPABASE_ANON_KEY || "')[1].split('"')[0]
            return url, key
    except:
        return None, None

url, key = get_creds()
if not url or not key:
    print("❌ Could not find Supabase credentials in scanner lib.")
    exit(1)

print(f"🔗 Connecting to Supabase: {url}")
supabase: Client = create_client(url, key)

def check_holders():
    print("📊 Checking Top 10 Holders in Supabase...")
    try:
        response = supabase.table("holders").select("*").order("balance", desc=True).limit(10).execute()
        if response.data:
            for i, h in enumerate(response.data):
                print(f"  #{i+1} {h['address'][:16]}... | Balance: {int(h['balance'])/10**8:.2f} $HOME")
        else:
            print("  ⚠️ No holders found in database yet.")
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    check_holders()
