
import requests
SB_URL = 'https://qmlcekoypbutzsliqqkm.supabase.co'
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"
headers = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}', 'Prefer': 'count=exact'}

for table in ["blocks", "transactions", "rewards"]:
    r = requests.get(f"{SB_URL}/rest/v1/{table}?limit=1", headers=headers)
    print(f"{table}: {r.headers.get('Content-Range')}")
