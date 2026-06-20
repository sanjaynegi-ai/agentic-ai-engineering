import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from comparison_no_framework.tools import calculate, get_weather
def test_calculator(): assert calculate('2 + 3 * 4').value == 14
def test_weather_fallback(monkeypatch):
    import requests
    monkeypatch.setattr(requests, 'get', lambda *a, **k: (_ for _ in ()).throw(requests.RequestException()))
    assert get_weather('Jaipur').live is False
