# Research Assistant Agent - OpenAI Agents SDK

This is the SDK rebuild of [`no_framework_projects/research_assistant_agent`](../../no_framework_projects/research_assistant_agent). Both versions answer from the same local Markdown notes, return the same `ResearchAnswer`, cite the selected file, and admit when evidence is missing. Study the retrieval logic in the no-framework version first.

## What stays the same

- Local-only evidence under `data/notes/`
- Deterministic ranking for offline comparison
- Grounded flag, citations, and an explicit insufficient-evidence answer

## What the SDK adds

- `build_agent()` declares grounded-answer instructions and typed output
- `run_live()` delegates bounded model execution to `Runner`
- The model-facing contract makes unsupported claims invalid rather than merely discouraged

## Run and verify

From this directory:

```bash
uv sync --group dev
uv run pytest
uv run python app.py
```

From the repository root, compare both implementations with:

```bash
uv run python -m evals.run_project_evals --project research_assistant_agent
```

Build with `docker build -t research-assistant-agent-sdk:local .`. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` only when adding a live UI path or calling `run_live()`.
