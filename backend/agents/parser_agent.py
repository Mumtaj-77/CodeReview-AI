import ast
import re
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ParsedCode:
    language: str
    functions: List[str]
    classes: List[str]
    imports: List[str]
    lines: int
    complexity: int
    raw_code: str

def detect_language(code: str) -> str:
    if "def " in code or "import " in code or "print(" in code:
        return "python"
    elif "function " in code or "const " in code or "let " in code:
        return "javascript"
    elif "public class" in code or "System.out" in code:
        return "java"
    return "python"  # default

def calculate_complexity(code: str) -> int:
    """Cyclomatic complexity approximation"""
    complexity = 1
    patterns = [
        r'\bif\b', r'\belif\b', r'\belse\b',
        r'\bfor\b', r'\bwhile\b', r'\btry\b',
        r'\bexcept\b', r'\band\b', r'\bor\b'
    ]
    for pattern in patterns:
        complexity += len(re.findall(pattern, code))
    return complexity

def extract_python_info(code: str) -> Dict[str, Any]:
    functions, classes, imports = [], [], []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend(a.name for a in node.names)
                else:
                    imports.append(node.module or "")
    except SyntaxError:
        pass
    return {"functions": functions, "classes": classes, "imports": imports}

def parse_code(code: str) -> ParsedCode:
    language = detect_language(code)
    info = extract_python_info(code) if language == "python" else {
        "functions": [], "classes": [], "imports": []
    }
    return ParsedCode(
        language=language,
        functions=info["functions"],
        classes=info["classes"],
        imports=info["imports"],
        lines=len(code.splitlines()),
        complexity=calculate_complexity(code),
        raw_code=code
    )

# ── Test ──
if __name__ == "__main__":
    test_code = """
import os
import sys

class UserManager:
    def get_user(self, id):
        user = db.find(id)
        return user.name

def divide(a, b):
    return a / b

password = 'abc123'
query = f"SELECT * FROM users WHERE id={password}"
"""
    result = parse_code(test_code)
    print(f"Language:   {result.language}")
    print(f"Functions:  {result.functions}")
    print(f"Classes:    {result.classes}")
    print(f"Imports:    {result.imports}")
    print(f"Lines:      {result.lines}")
    print(f"Complexity: {result.complexity}")