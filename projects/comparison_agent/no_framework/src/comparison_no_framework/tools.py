import ast
import operator
from datetime import UTC, datetime
from zoneinfo import ZoneInfo
import requests
from .config import DATA_FILE
from .schemas import CalculationResult, SearchResult, TimeResult, WeatherResult
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}
def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression): return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, int | float): return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in OPS: return float(OPS[type(node.op)](_eval(node.left), _eval(node.right)))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS: return float(OPS[type(node.op)](_eval(node.operand)))
    raise ValueError("Only numeric arithmetic is allowed")
def calculate(expression: str) -> CalculationResult:
    if len(expression) > 100: raise ValueError("Expression too long")
    return CalculationResult(expression=expression, value=_eval(ast.parse(expression, mode="eval")))
def get_current_time(timezone: str = "UTC") -> TimeResult:
    try: now = datetime.now(ZoneInfo(timezone))
    except Exception: now, timezone = datetime.now(UTC), "UTC"
    return TimeResult(timezone=timezone, iso_time=now.isoformat())
def get_weather(city: str) -> WeatherResult:
    try:
        response = requests.get(f"https://wttr.in/{city}", params={"format": "j1"}, timeout=3)
        response.raise_for_status(); current = response.json()["current_condition"][0]
        precip = float(current.get("precipMM", 0)); desc = current["weatherDesc"][0]["value"]
        return WeatherResult(city=city, summary=desc, umbrella_recommended=precip > 0, live=True)
    except (requests.RequestException, KeyError, ValueError, TypeError):
        return WeatherResult(city=city, summary="Live weather unavailable; check a trusted forecast before departure.", umbrella_recommended=True, live=False)
def search_local_notes(query: str) -> SearchResult:
    lines = DATA_FILE.read_text(encoding="utf-8").splitlines()
    terms = {term.lower() for term in query.split() if len(term) > 2}
    matches = [line.strip() for line in lines if line.strip() and any(term in line.lower() for term in terms)]
    return SearchResult(query=query, matches=matches[:5])
