import requests

print("=== HISTORY ===")
r = requests.get("http://localhost:8000/history")
import json
print(json.dumps(r.json(), indent=2))

print("\n=== METRICS ===")
r = requests.get("http://localhost:8000/metrics")
print(json.dumps(r.json(), indent=2))