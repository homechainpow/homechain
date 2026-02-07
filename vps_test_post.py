
import requests
url = "https://qmlcekoypbutzsliqqkm.supabase.co/rest/v1/blocks"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"
headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
data = {"id": 9999, "hash": "testFromVPS", "validator": "VPS", "timestamp": "2026-02-06 13:00:00"}
r = requests.post(url, headers=headers, json=data)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
