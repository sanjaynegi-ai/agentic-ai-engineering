# uv setup
```bash
uv init agentic-ai-engineering
cd agentic-ai-engineering
uv sync
uv add openai python-dotenv pydantic requests httpx gradio rich
uv add --dev jupyter ipykernel pytest ruff mypy
uv run python --version
uv run pytest
uv run ruff check .
```
Activate only when useful: PowerShell `.venv\Scripts\Activate.ps1`; CMD `.venv\Scripts\activate.bat`; macOS/Linux `source .venv/bin/activate`.

```bash
uv run python -m ipykernel install --user --name agentic-ai-engineering --display-name "Agentic AI Engineering"
uv run jupyter lab
uv run jupyter kernelspec uninstall agentic-ai-engineering
```
Prefer `uv run` in scripts and CI because it makes the intended environment explicit.
