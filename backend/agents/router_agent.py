import torch
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dataclasses import dataclass
from typing import Literal

FAST_MODEL = "openai/gpt-oss-20b"
POWERFUL_MODEL = "qwen/qwen3.6-27b"
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "models", "codebert-finetuned")

@dataclass
class RouteDecision:
    severity: str
    confidence: float
    model_selected: str
    reasoning: str

class RouterAgent:
    def __init__(self):
        print("Loading CodeBERT router...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        self.model.eval()
        if torch.cuda.is_available():
            self.model = self.model.cuda()
        print("Router ready.")

    def route(self, code: str) -> RouteDecision:
        # Tokenize
        inputs = self.tokenizer(
            code,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt"
        )

        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            confidence, predicted = torch.max(probs, dim=-1)

        labels = ["critical", "medium", "low"]
        severity = labels[predicted.item()]
        confidence_score = confidence.item()

        # Route decision
        if severity == "critical" or confidence_score < 0.75:
            model = POWERFUL_MODEL
            reasoning = f"severity={severity}, confidence={confidence_score:.2f} → powerful model"
        else:
            model = FAST_MODEL
            reasoning = f"severity={severity}, confidence={confidence_score:.2f} → fast model"

        return RouteDecision(
            severity=severity,
            confidence=confidence_score,
            model_selected=model,
            reasoning=reasoning
        )

# ── Test ──
if __name__ == "__main__":
    router = RouterAgent()

    test_cases = [
        # Critical
        "password = 'abc123'\ndb.execute(f'SELECT * FROM users WHERE pass={password}')",
        # Medium
        "def get_user(id):\n    user = db.find(id)\n    return user.name",
        # Low
        "def calculatePrice(itemList):\n    totalPrice = 0\n    return totalPrice",
    ]

    for i, code in enumerate(test_cases):
        decision = router.route(code)
        print(f"\nTest {i+1}:")
        print(f"  Severity:  {decision.severity}")
        print(f"  Confidence:{decision.confidence:.2f}")
        print(f"  Model:     {decision.model_selected}")
        print(f"  Reasoning: {decision.reasoning}")