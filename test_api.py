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

print("Testing CodeReview AI API...")

# Submit review
response = requests.post(f"{BASE_URL}/review", json={
    "code": test_code,
    "filename": "test.py"
})
print(f"Status: {response.status_code}")
data = response.json()
print(f"Job ID: {data['job_id']}")

# Poll for result
job_id = data['job_id']
print("\nWaiting for review...")

for i in range(30):
    time.sleep(3)
    result = requests.get(f"{BASE_URL}/review/{job_id}")
    status = result.json()['status']
    print(f"  Status: {status}")
    if status == "completed":
        report = result.json()['report']
        print("\n=== REVIEW COMPLETE ===")
        print(json.dumps(report['summary'], indent=2))
        print(f"\nBugs: {len(report['bugs'])}")
        print(f"Security: {len(report['security_issues'])}")
        print(f"Fixes: {len(report['fixes'])}")
        break
    elif status == "failed":
        print(f"Failed: {result.json()}")
        break