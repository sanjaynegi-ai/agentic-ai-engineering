import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_expected_notebook_count(): assert len(list((ROOT/'notebooks').rglob('*.ipynb'))) == 18
def test_notebooks_have_real_cells():
    for path in (ROOT/'notebooks').rglob('*.ipynb'):
        data=json.loads(path.read_text(encoding='utf-8')); assert len(data['cells']) >= 8
def test_local_env_is_ignored():
    assert ".env" in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
