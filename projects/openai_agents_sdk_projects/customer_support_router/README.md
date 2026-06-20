# Customer Support Router - OpenAI Agents SDK

This is the SDK rebuild of [`no_framework_projects/customer_support_router`](../../no_framework_projects/customer_support_router). Both versions classify the same tickets, use the same route values and escalation rules, and stop at a draft response. Study the no-framework version first.

## What stays the same

- Billing, technical, account, sales, and human-review routes
- Deterministic confidence, ambiguity handling, and risk escalation
- Draft-only behavior: the application never sends a reply or changes an account

## What the SDK adds

- `build_agent()` binds routing instructions to the typed `RoutingResult`
- `run_live()` uses `Runner` with an eight-turn limit
- The output contract includes the draft that a human would review

## Run and verify

From this directory:

```bash
uv sync --group dev
uv run pytest
uv run python app.py
```

From the repository root, compare both implementations with:

```bash
uv run python -m evals.run_project_evals --project customer_support_router
```

Build with `docker build -t customer-support-router-sdk:local .`. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` only when adding a live UI path or calling `run_live()`.
