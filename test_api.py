import requests
import json
import time

BASE_URL = "http://localhost:8000"

test_code = """
def get_user(user_id):
    password = "admin123"
    query = f"SELECT * FROM users WHERE id={user_id}"
    db.execute(query)

def divide(a, b):
    return a / b
"""

res = requests.post(f"{BASE_URL}/review", json={"code": test_code, "filename": "test.py"})
job_id = res.json()['job_id']
print(f"Job ID: {job_id}")

for i in range(20):
    time.sleep(3)
    result = requests.get(f"{BASE_URL}/review/{job_id}").json()
    status = result['status']
    print(f"Status: {status}")
    if status == "completed":
        summary = result['report']['summary']
        print(json.dumps(summary, indent=2))
        print(f"Fixes: {len(result['report']['fixes'])}")
        break