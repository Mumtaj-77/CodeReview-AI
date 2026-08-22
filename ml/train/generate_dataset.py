import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

prompts = [
    ("critical", "security", "Generate a Python code snippet with a critical security vulnerability like SQL injection, hardcoded credentials, or XSS. Return ONLY the code, no explanation."),
    ("critical", "bug", "Generate a Python code snippet with a critical bug like division by zero, null pointer, or infinite loop. Return ONLY the code, no explanation."),
    ("medium", "bug", "Generate a Python code snippet with a medium severity bug like memory leak, unused variable, or wrong logic. Return ONLY the code, no explanation."),
    ("low", "style", "Generate a Python code snippet with only style issues like bad naming, missing docstrings, or unused imports. Return ONLY the code, no explanation."),
]

samples = []
existing = json.load(open("datasets/bug_dataset.json"))
samples.extend(existing)

print(f"Starting with {len(samples)} samples")
print("Generating 500 more via Groq...")

for i in range(500):
    label, category, prompt = prompts[i % len(prompts)]
    try:
        response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system", 
            "content": "You are a code generator. Return ONLY raw Python code. No markdown, no backticks, no explanation. Just pure Python code."
        },
        {
            "role": "user", 
            "content": prompt
        }
    ],
    max_tokens=200,
    temperature=0.7,
    tool_choice="none"
)
        code = response.choices[0].message.content.strip()
        code = code.replace("```python", "").replace("```", "").strip()
        
        samples.append({
            "id": len(samples),
            "code": code,
            "label": label,
            "category": category
        })
        
        if (i+1) % 50 == 0:
            print(f"Generated {i+1}/500 samples...")
            
    except Exception as e:
        print(f"Skipping {i}: {str(e)[:50]}")
        continue

with open("datasets/bug_dataset.json", "w") as f:
    json.dump(samples, f, indent=2)

from collections import Counter
labels = Counter([s["label"] for s in samples])
print(f"\nTotal samples: {len(samples)}")
print(f"Distribution: {labels}")
print("Dataset saved!")