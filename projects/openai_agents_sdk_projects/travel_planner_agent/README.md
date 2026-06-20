# Travel Planner Agent - OpenAI Agents SDK

This is the SDK rebuild of [`no_framework_projects/travel_planner_agent`](../../no_framework_projects/travel_planner_agent). Both versions accept the same travel request and return the same typed itinerary contract. Study the no-framework version first, then use this version to identify what `Agent`, `Runner`, typed output, and SDK turn limits replace.

## What stays the same

- Supported cities, traveler/day parsing, budget formula, source note, and safety boundary
- Deterministic `run()` path for free offline tests and comparison
- No bookings, purchases, or claims that estimates are live quotes

## What the SDK adds

- `build_agent()` declares instructions and `Itinerary` as the output type
- `run_live()` delegates the bounded model loop to `Runner.run(..., max_turns=8)`
- The agent prompt coordinates itinerary, budget, and packing concerns behind one contract

## Run and verify

From this directory:

```bash
uv sync --group dev
uv run pytest
uv run python app.py
```

From the repository root, compare both implementations with:

```bash
uv run python -m evals.run_project_evals --project travel_planner_agent
```

Build with `docker build -t travel-planner-agent-sdk:local .`. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` only when adding a live UI path or calling `run_live()`.
