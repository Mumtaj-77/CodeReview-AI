import os
from groq import Groq
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
import json
import re

load_dotenv()

@dataclass
class Fix:
    line: int
    original: str
    fixed: str
    explanation: str
    principle: str
    learn_more: str

def clean_llm_response(content: str) -> str:
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    content = re.sub(r'```json|```', '', content)
    content = content.strip()
    start = content.find('[')
    end = content.rfind(']') + 1
    if start != -1 and end > start:
        content = content[start:end]
    return content

class FixSuggesterAgent:
    def __init__(self, model: str):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model

    def suggest(self, code: str, bugs: list) -> List[Fix]:
        bugs_summary = "\n".join([
            f"Line {b.line}: {b.description}"
            for b in bugs
        ])

        prompt = f"""Fix these bugs in the code. Return ONLY JSON array.

Code:
{code}

Bugs found:
{bugs_summary}

Return JSON array:
[{{
  "line": 5,
  "original": "original code line",
  "fixed": "corrected code line",
  "explanation": "why this fixes it",
  "principle": "SOLID/DRY/Security principle violated",
  "learn_more": "https://relevant-docs-link.com"
}}]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Senior developer. Output ONLY valid JSON arrays. No markdown. No thinking. Just JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.1
            )

            content = response.choices[0].message.content
            cleaned = clean_llm_response(content)
            fixes_data = json.loads(cleaned)
            return [Fix(**f) for f in fixes_data if isinstance(f, dict)]

        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return []
        except Exception as e:
            print(f"Fix suggestion error: {e}")
            return []


class ExplainerAgent:
    def __init__(self, model: str):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model

    def explain(self, bug_description: str, fix: str) -> str:
        prompt = f"""Explain this bug and fix to a junior developer in 3 sentences max.
Bug: {bug_description}
Fix: {fix}
Be clear, educational, and encouraging."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a patient senior developer teaching juniors."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            content = response.choices[0].message.content
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
            return content.strip()
        except Exception as e:
            return f"Explanation unavailable: {e}"


# ── Test ──
if __name__ == "__main__":
    from router_agent import RouterAgent
    from bug_detector_agent import BugDetectorAgent, Bug

    test_code = """
def get_user(user_id):
    password = "admin123"
    query = f"SELECT * FROM users WHERE id={user_id}"
    db.execute(query)

def divide(a, b):
    return a / b
"""

    router = RouterAgent()
    decision = router.route(test_code)

    detector = BugDetectorAgent(model=decision.model_selected)
    bugs = detector.detect(test_code)
    print(f"Bugs found: {len(bugs)}")

    fixer = FixSuggesterAgent(model=decision.model_selected)
    fixes = fixer.suggest(test_code, bugs)

    explainer = ExplainerAgent(model=decision.model_selected)

    print(f"\nFixes + Explanations:\n")
    for fix in fixes:
        print(f"Line {fix.line}:")
        print(f"  Original:  {fix.original}")
        print(f"  Fixed:     {fix.fixed}")
        print(f"  Principle: {fix.principle}")
        explanation = explainer.explain(fix.original, fix.fixed)
        print(f"  Learn:     {explanation[:150]}")
        print()