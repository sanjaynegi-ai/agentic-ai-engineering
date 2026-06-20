import ast
import operator
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
from agents import function_tool
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.USub: operator.neg}
DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "local_notes" / "travel_india.md"
def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression): return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, int | float): return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in OPS: return float(OPS[type(node.op)](_eval(node.left), _eval(node.right)))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS: return float(OPS[type(node.op)](_eval(node.operand)))
    raise ValueError("Only basic numeric arithmetic is allowed")
@function_tool
def get_weather(city: str) -> str:
    """Get current weather or a clear fallback for a city."""
    try:
        response = requests.get(f"https://wttr.in/{city}", params={"format": "j1"}, timeout=3); response.raise_for_status()
        current = response.json()["current_condition"][0]; return f"{city}: {current['weatherDesc'][0]['value']}"
    except (requests.RequestException, KeyError, ValueError, TypeError): return f"{city}: live weather unavailable; check a trusted forecast"
@function_tool
def calculate(expression: str) -> str:
    """Evaluate safe numeric arithmetic for a budget."""
    if len(expression) > 100: raise ValueError("Expression too long")
    return str(_eval(ast.parse(expression, mode="eval")))
@function_tool
def get_current_time(timezone: str = "UTC") -> str:
    """Get current time in an IANA timezone."""
    try: return datetime.now(ZoneInfo(timezone)).isoformat()
    except Exception: return datetime.now(UTC).isoformat()
@function_tool
def search_local_notes(query: str) -> str:
    """Search trusted local India travel notes."""
    terms = {term.lower() for term in query.split() if len(term) > 2}
    lines = DATA_FILE.read_text(encoding="utf-8").splitlines()
    matches = [line for line in lines if any(term in line.lower() for term in terms)]
    return "\n".join(matches[:5]) or "No local note matched."
