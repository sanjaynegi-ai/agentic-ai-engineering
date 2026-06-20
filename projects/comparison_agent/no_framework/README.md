# No-framework Travel Agent

## What it does
Makes the observe-decide-act loop, registry, validation, limits, memory, and events visible.

## Architecture
Gradio calls a bounded agent runtime. Typed tools and schemas sit behind prompt files; guardrails validate input and output; tests use deterministic boundaries.

## Tools and prompts
See `src/` for tool code and `prompts/` for reusable instructions.

## Run locally
```bash
copy .env.example .env
uv sync --group dev
uv run python app.py
uv run pytest
```

## Docker
```bash
docker compose up --build
```

## Environment
Configure `OPENAI_API_KEY`, `OPENAI_MODEL`, and runtime limits from `.env.example`.

## Limitations
No live booking, weather may fall back, local notes are deliberately small, and live model tests are opt-in.

## Evaluation

From the repository root, run `uv run python -m evals.run_evals --implementation no_framework`. Add `--mode live` to execute the real model-backed agent. The shared golden cases grade tools, refusals, prohibited claims, tool budgets, and final budget constraints.

## Extensions
Add richer trusted data, approval gates, model-judge rubrics, persistent production storage, and deployment monitoring.
