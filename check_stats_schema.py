
import requests
SB_URL = "https://qmlcekoypbutzsliqqkm.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFtbGNla295cGJ1dHpzbGlxcWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDI1OTk4MCwiZXhwIjoyMDg1ODM1OTgwfQ.B93GWkvFddjWV9BMZXdgoYv8YYV22TiaA2lPutQd8a4"
headers = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}

def check_stats_schema():
    r = requests.get(f"{SB_URL}/rest/v1/stats?limit=1", headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data:
            print("Stats Columns:")
            for k in data[0].keys():
                print(f"- {k}")
        else:
            print("Stats Table Empty (Cannot determine schema from empty table via REST)")
            # Try to post a dummy to see if it accepts 'difficulty'
            payload = {"id": 999, "difficulty": "test"}
            headers_post = headers.copy()
            headers_post['Prefer'] = 'return=minimal'
            r2 = requests.post(f"{SB_URL}/rest/v1/stats", headers=headers_post, json=payload)
            if r2.status_code == 201:
                print("Stats Table accepts 'difficulty' column.")
                # clean up
                requests.delete(f"{SB_URL}/rest/v1/stats?id=eq.999", headers=headers)
            else:
                print(f"Stats Table REJECTED 'difficulty': {r2.status_code} - {r2.text}")
    else:
        print(f"Error: {r.status_code} - {r.text}")

if __name__ == "__main__":
    check_stats_schema()
