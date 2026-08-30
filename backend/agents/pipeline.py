import os
import sys
import time
from typing import TypedDict, List, Any
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.agents.parser_agent import parse_code, ParsedCode
from backend.agents.router_agent import RouterAgent
from backend.agents.bug_detector_agent import BugDetectorAgent, Bug
from backend.agents.security_agent import SecurityScannerAgent
from backend.agents.fix_agent import FixSuggesterAgent, ExplainerAgent

# ── Pipeline State ──
class ReviewState(TypedDict):
    code: str
    parsed: Any
    route_decision: Any
    bugs: List[Any]
    security_issues: List[Any]
    fixes: List[Any]
    explanations: List[str]
    report: dict
    start_time: float

# ── Initialize agents ──
router = RouterAgent()

# ── Agent nodes ──
def parse_node(state: ReviewState) -> ReviewState:
    print("→ Parser Agent running...")
    parsed = parse_code(state["code"])
    return {**state, "parsed": parsed}

def route_node(state: ReviewState) -> ReviewState:
    print("→ Router Agent running...")
    decision = router.route(state["code"])
    print(f"  Model selected: {decision.model_selected}")
    print(f"  Severity: {decision.severity} ({decision.confidence:.2f})")
    return {**state, "route_decision": decision}

def bug_detect_node(state: ReviewState) -> ReviewState:
    print("→ Bug Detector Agent running...")
    model = state["route_decision"].model_selected
    detector = BugDetectorAgent(model=model)
    bugs = detector.detect(state["code"])
    print(f"  Found {len(bugs)} bugs")
    return {**state, "bugs": bugs}

def security_node(state: ReviewState) -> ReviewState:
    print("→ Security Scanner Agent running...")
    model = state["route_decision"].model_selected
    scanner = SecurityScannerAgent(model=model)
    issues = scanner.scan(state["code"])
    print(f"  Found {len(issues)} security issues")
    return {**state, "security_issues": issues}

def fix_node(state: ReviewState) -> ReviewState:
    print("→ Fix Suggester Agent running...")
    model = state["route_decision"].model_selected
    fixer = FixSuggesterAgent(model=model)
    fixes = fixer.suggest(state["code"], state["bugs"])
    print(f"  Generated {len(fixes)} fixes")
    return {**state, "fixes": fixes}

def explain_node(state: ReviewState) -> ReviewState:
    print("→ Explainer Agent running...")
    model = state["route_decision"].model_selected
    explainer = ExplainerAgent(model=model)
    explanations = []
    for fix in state["fixes"]:
        exp = explainer.explain(fix.original, fix.fixed)
        explanations.append(exp)
        time.sleep(1)
    return {**state, "explanations": explanations}

def report_node(state: ReviewState) -> ReviewState:
    print("→ Report Generator running...")
    elapsed = time.time() - state["start_time"]

    report = {
        "summary": {
            "total_bugs": len(state["bugs"]),
            "total_security_issues": len(state["security_issues"]),
            "total_fixes": len(state["fixes"]),
            "language": state["parsed"].language,
            "lines_of_code": state["parsed"].lines,
            "complexity": state["parsed"].complexity,
            "model_used": state["route_decision"].model_selected,
            "severity": state["route_decision"].severity,
            "review_time_seconds": round(elapsed, 2)
        },
        "bugs": [
            {
                "line": b.line,
                "severity": b.severity,
                "category": b.category,
                "description": b.description,
                "fix": b.fix
            }
            for b in state["bugs"]
        ],
        "security_issues": [
            {
                "line": s.line,
                "vulnerability": s.vulnerability,
                "severity": s.severity,
                "description": s.description,
                "fix": s.fix
            }
            for s in state["security_issues"]
        ],
        "fixes": [
            {
                "line": f.line,
                "original": f.original,
                "fixed": f.fixed,
                "principle": f.principle,
                "explanation": state["explanations"][i] if i < len(state["explanations"]) else ""
            }
            for i, f in enumerate(state["fixes"])
        ]
    }

    return {**state, "report": report}

# ── Build Graph ──
def build_pipeline():
    graph = StateGraph(ReviewState)

    graph.add_node("parse", parse_node)
    graph.add_node("route", route_node)
    graph.add_node("detect_bugs", bug_detect_node)
    graph.add_node("scan_security", security_node)
    graph.add_node("suggest_fixes", fix_node)
    graph.add_node("explain", explain_node)
    graph.add_node("report", report_node)

    graph.set_entry_point("parse")
    graph.add_edge("parse", "route")
    graph.add_edge("route", "detect_bugs")
    graph.add_edge("detect_bugs", "scan_security")
    graph.add_edge("scan_security", "suggest_fixes")
    graph.add_edge("suggest_fixes", "explain")
    graph.add_edge("explain", "report")
    graph.add_edge("report", END)

    return graph.compile()

# ── Test ──
if __name__ == "__main__":
    import json

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

    print("=" * 50)
    print("CodeReview AI — Full Pipeline Test")
    print("=" * 50)

    pipeline = build_pipeline()

    initial_state = ReviewState(
        code=test_code,
        parsed=None,
        route_decision=None,
        bugs=[],
        security_issues=[],
        fixes=[],
        explanations=[],
        report={},
        start_time=time.time()
    )

    result = pipeline.invoke(initial_state)
    report = result["report"]

    print("\n" + "=" * 50)
    print("REVIEW COMPLETE")
    print("=" * 50)
    print(json.dumps(report["summary"], indent=2))
    print(f"\nBugs: {len(report['bugs'])}")
    print(f"Security: {len(report['security_issues'])}")
    print(f"Fixes: {len(report['fixes'])}")