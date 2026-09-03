import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from backend.agents.parser_agent import parse_code
from backend.agents.router_agent import RouterAgent
from backend.agents.bug_detector_agent import BugDetectorAgent
from backend.agents.security_agent import SecurityScannerAgent

# ── Parser Agent Tests ──
def test_parser_detects_python():
    code = "def hello():\n    print('hello')"
    result = parse_code(code)
    assert result.language == "python"

def test_parser_extracts_functions():
    code = "def foo():\n    pass\ndef bar():\n    pass"
    result = parse_code(code)
    assert "foo" in result.functions
    assert "bar" in result.functions

def test_parser_extracts_imports():
    code = "import os\nimport sys\ndef main():\n    pass"
    result = parse_code(code)
    assert "os" in result.imports
    assert "sys" in result.imports

def test_parser_counts_lines():
    code = "line1\nline2\nline3"
    result = parse_code(code)
    assert result.lines == 3

def test_parser_detects_javascript():
    code = "const x = 1;\nfunction hello() { return x; }"
    result = parse_code(code)
    assert result.language == "javascript"

# ── Router Agent Tests ──
@pytest.fixture(scope="module")
def router():
    return RouterAgent()

def test_router_loads(router):
    assert router is not None
    assert router.model is not None

def test_router_critical_code(router):
    code = "password = 'abc123'\ndb.execute(f'SELECT * FROM users WHERE id={user_id}')"
    decision = router.route(code)
    assert decision.severity in ["critical", "medium", "low"]
    assert decision.confidence > 0.0
    assert decision.model_selected is not None

def test_router_returns_model(router):
    code = "def add(a, b):\n    return a + b"
    decision = router.route(code)
    assert "compound" in decision.model_selected or "qwen" in decision.model_selected or "gpt" in decision.model_selected

def test_router_confidence_range(router):
    code = "x = 1\ny = 2\nprint(x + y)"
    decision = router.route(code)
    assert 0.0 <= decision.confidence <= 1.0

# ── Security Scanner Tests ──
def test_security_detects_hardcoded_password():
    scanner = SecurityScannerAgent(model="groq/compound-mini")
    code = "password = 'admin123'"
    issues = scanner._regex_scan(code)
    assert len(issues) > 0
    vulns = [i.vulnerability for i in issues]
    assert "HARDCODED_PASSWORD" in vulns

def test_security_detects_sql_injection():
    scanner = SecurityScannerAgent(model="groq/compound-mini")
    code = 'query = f"SELECT * FROM users WHERE id={user_id}"'
    issues = scanner._regex_scan(code)
    assert len(issues) > 0

def test_security_detects_hardcoded_api_key():
    scanner = SecurityScannerAgent(model="groq/compound-mini")
    code = "api_key = 'sk-abc123'"
    issues = scanner._regex_scan(code)
    assert len(issues) > 0

def test_security_clean_code():
    scanner = SecurityScannerAgent(model="groq/compound-mini")
    code = "def add(a, b):\n    return a + b"
    issues = scanner._regex_scan(code)
    assert len(issues) == 0

# ── Integration Test ──
def test_full_parser_to_router(router):
    code = """
import os
def get_user(user_id):
    password = "admin123"
    query = f"SELECT * FROM users WHERE id={user_id}"
    db.execute(query)
"""
    parsed = parse_code(code)
    assert parsed.language == "python"
    assert len(parsed.functions) > 0

    decision = router.route(code)
    assert decision.severity is not None
    assert decision.model_selected is not None