import re
import json

def clean_llm_response(content: str) -> str:
    """Remove thinking tags, markdown, extract JSON"""
    # Remove <think> blocks
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    # Remove markdown
    content = re.sub(r'```json|```', '', content)
    content = content.strip()
    # Extract JSON array or object
    start = content.find('[')
    end = content.rfind(']') + 1
    if start != -1 and end > start:
        content = content[start:end]
    return content

def parse_json_safe(content: str) -> list:
    """Parse JSON safely"""
    try:
        cleaned = clean_llm_response(content)
        return json.loads(cleaned)
    except Exception as e:
        print(f"JSON parse error: {e}")
        return []