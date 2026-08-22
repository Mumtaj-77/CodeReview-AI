import os
from groq import Groq
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
import json
import re

load_dotenv()

@dataclass
class Bug:
    line: int
    severity: str
    category: str
    description: str
    fix: str

class BugDetectorAgent:
    def __init__(self, model: str):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model

    def detect(self, code: str) -> List[Bug]:
        prompt = f"""You are a code reviewer. Find ALL bugs in this code.

Code to review:
{code}

Return ONLY a JSON array. No markdown. No explanation. Just JSON.
Format: [{{"line": 1, "severity": "critical", "category": "security", "description": "explain bug", "fix": "how to fix"}}]

Find at least 3 issues if they exist. Return [] only if code is perfect."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior code reviewer. You ONLY output valid JSON arrays. Never use markdown. Never explain. Just output the JSON array directly."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )

            content = response.choices[0].message.content.strip()
            print(f"Raw response: {content[:200]}")

            # Clean response
            content = re.sub(r'```json|```', '', content).strip()

            # Find JSON array in response
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                content = content[start:end]

            bugs_data = json.loads(content)
            return [Bug(**b) for b in bugs_data]

        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Content was: {content}")
            return []
        except Exception as e:
            print(f"Bug detection error: {e}")
            return []

# ── Test ──
if __name__ == "__main__":
    from router_agent import RouterAgent

    test_code = """
import os

def get_user(user_id):
    password = "admin123"
    query = f"SELECT * FROM users WHERE id={user_id}"
    db.execute(query)

def divide(a, b):
    return a / b

def processData(DataList):
    totalValue = 0
    for Item in DataList:
        totalValue += Item
    return totalValue
"""

    router = RouterAgent()
    decision = router.route(test_code)
    print(f"Router selected: {decision.model_selected}")

    detector = BugDetectorAgent(model=decision.model_selected)
    bugs = detector.detect(test_code)

    print(f"\nFound {len(bugs)} bugs:\n")
    for bug in bugs:
        print(f"Line {bug.line}: [{bug.severity.upper()}] {bug.description}")
        print(f"  Fix: {bug.fix}\n")