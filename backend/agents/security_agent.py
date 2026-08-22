import os
import re
from groq import Groq
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
import json

load_dotenv()

@dataclass
class SecurityIssue:
    line: int
    vulnerability: str
    severity: str
    description: str
    fix: str

class SecurityScannerAgent:
    def __init__(self, model: str):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model

    def _regex_scan(self, code: str) -> List[SecurityIssue]:
        """Fast rule-based security scan"""
        issues = []
        lines = code.splitlines()

        patterns = [
            (r'password\s*=\s*["\']', "HARDCODED_PASSWORD", "critical",
             "Hardcoded password detected", "Use environment variables"),
            (r'api_key\s*=\s*["\']', "HARDCODED_API_KEY", "critical",
             "Hardcoded API key detected", "Use os.getenv()"),
            (r'secret\s*=\s*["\']', "HARDCODED_SECRET", "critical",
             "Hardcoded secret detected", "Use environment variables"),
            (r'f["\'].*SELECT.*{', "SQL_INJECTION", "critical",
             "SQL injection via f-string", "Use parameterized queries"),
            (r'eval\(', "CODE_INJECTION", "critical",
             "eval() is dangerous", "Never use eval() on user input"),
            (r'exec\(', "CODE_INJECTION", "critical",
             "exec() is dangerous", "Avoid exec() on untrusted input"),
            (r'pickle\.loads\(', "INSECURE_DESERIALIZATION", "high",
             "Insecure deserialization", "Use JSON instead of pickle"),
            (r'subprocess\.call\(.*shell=True', "COMMAND_INJECTION", "critical",
             "Shell injection risk", "Use shell=False"),
            (r'md5\(|sha1\(', "WEAK_CRYPTO", "medium",
             "Weak cryptography", "Use SHA-256 or bcrypt"),
            (r'http://', "INSECURE_PROTOCOL", "medium",
             "HTTP used instead of HTTPS", "Always use HTTPS"),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, vuln, severity, desc, fix in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        line=i,
                        vulnerability=vuln,
                        severity=severity,
                        description=desc,
                        fix=fix
                    ))

        return issues

    def scan(self, code: str) -> List[SecurityIssue]:
        # First do fast regex scan
        regex_issues = self._regex_scan(code)

        # Then LLM deep scan
        prompt = f"""Scan this code for security vulnerabilities only.
Return ONLY JSON array. No markdown. No explanation.

Code:
{code}

Format: [{{"line": 1, "vulnerability": "TYPE", "severity": "critical/high/medium/low", "description": "what's wrong", "fix": "how to fix"}}]
Return [] if no security issues found."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Security expert. Output ONLY valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.1
            )

            content = response.choices[0].message.content.strip()
            # Remove thinking tags
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
            content = re.sub(r'```json|```', '', content).strip()
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                content = content[start:end]

            llm_issues = [SecurityIssue(**i) for i in json.loads(content)]

        except Exception as e:
            print(f"LLM scan error: {e}")
            llm_issues = []

        # Combine both
        all_issues = regex_issues + llm_issues
        seen_lines = set()
        unique_issues = []
        for issue in all_issues:
            if issue.line not in seen_lines:
                unique_issues.append(issue)
                seen_lines.add(issue.line)

        return unique_issues

# ── Test ──
if __name__ == "__main__":
    test_code = """
import os
import pickle
import subprocess

def get_user(user_id):
    password = "admin123"
    api_key = "sk-abc123secret"
    query = f"SELECT * FROM users WHERE id={user_id}"
    db.execute(query)

def run_command(cmd):
    subprocess.call(cmd, shell=True)

def load_data(filename):
    with open(filename, 'rb') as f:
        return pickle.loads(f.read())

url = "http://api.example.com/data"
"""

    scanner = SecurityScannerAgent(model="groq/compound-mini")
    issues = scanner.scan(test_code)

    print(f"Found {len(issues)} security issues:\n")
    for issue in issues:
        print(f"Line {issue.line}: [{issue.severity.upper()}] {issue.vulnerability}")
        print(f"  {issue.description}")
        print(f"  Fix: {issue.fix}\n")