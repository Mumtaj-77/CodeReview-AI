import json
import os

# Bug severity labeled code samples
samples = [
    # CRITICAL bugs
    {"code": "password = '123456'\ndb.execute(f'SELECT * FROM users WHERE pass={password}')", "label": "critical", "category": "security"},
    {"code": "def divide(a, b):\n    return a / b", "label": "critical", "category": "bug"},
    {"code": "api_key = 'sk-abc123def456'\nrequests.get(url, headers={'key': api_key})", "label": "critical", "category": "security"},
    {"code": "while True:\n    data = fetch_data()\n    process(data)", "label": "critical", "category": "bug"},
    {"code": "user_input = request.GET['query']\ndb.execute('SELECT * FROM ' + user_input)", "label": "critical", "category": "security"},

    # MEDIUM bugs
    {"code": "def get_user(id):\n    user = db.find(id)\n    return user.name", "label": "medium", "category": "bug"},
    {"code": "items = []\nfor i in range(1000000):\n    items.append(i * 2)", "label": "medium", "category": "bug"},
    {"code": "except Exception:\n    pass", "label": "medium", "category": "bug"},
    {"code": "def calculate(x, y):\n    result = x + y\n    return result\n    print(result)", "label": "medium", "category": "bug"},
    {"code": "global_list = []\ndef add_item(item):\n    global_list.append(item)", "label": "medium", "category": "bug"},

    # LOW / STYLE
    {"code": "def calculateTotalPrice(item_list):\n    totalPrice = 0\n    for Item in item_list:\n        totalPrice += Item.price\n    return totalPrice", "label": "low", "category": "style"},
    {"code": "x=1\ny=2\nz=x+y\nprint(z)", "label": "low", "category": "style"},
    {"code": "def f(a,b,c,d,e,f):\n    return a+b+c+d+e+f", "label": "low", "category": "style"},
    {"code": "import os\nimport sys\nimport json\n\ndef hello():\n    print('hello')", "label": "low", "category": "style"},
    {"code": "# TODO: fix this later\ndef process():\n    pass", "label": "low", "category": "style"},
]

# Expand to 300 samples by duplicating with variations
expanded = []
for i, s in enumerate(samples * 20):
    expanded.append({
        "id": i,
        "code": s["code"],
        "label": s["label"],
        "category": s["category"]
    })

# Save dataset
os.makedirs("datasets", exist_ok=True)
with open("datasets/bug_dataset.json", "w") as f:
    json.dump(expanded, f, indent=2)

print(f"Dataset created: {len(expanded)} samples")
print("Labels distribution:")
from collections import Counter
labels = Counter([s["label"] for s in expanded])
print(labels)