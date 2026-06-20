# OpenAI Agents SDK Travel Team

## What it does
Uses SDK agents, typed function tools, handoffs, an input guardrail, structured itinerary output, sessions, and tracing.

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

From the repository root, run `uv run python -m evals.run_evals --implementation openai_agents_sdk`. Add `--mode live` to execute the real SDK agent team. Handoffs are captured as trajectory evidence alongside shared tool, safety, budget, and final-result checks.

## Extensions
Add richer trusted data, approval gates, model-judge rubrics, persistent production storage, and deployment monitoring.
