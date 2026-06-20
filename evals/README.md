# Agent evaluation harness

This folder evaluates the two travel-agent implementations against the same golden behavioral cases. It grades final behavior and execution trajectory rather than comparing answers word for word.

## Files

- `data/travel_planning_cases.jsonl` contains version-controlled golden cases.
- `fixtures/` contains deterministic recorded runs used to teach the graders and protect CI without API cost.
- `models.py` defines typed cases, traces, grades, and reports.
- `graders.py` implements deterministic checks.
- `adapters.py` connects the harness to both live comparison projects.
- `run_evals.py` runs offline or optional live evaluation.
- `reports/` contains generated reports and is ignored by Git.

## Offline evaluation

```bash
uv run python -m evals.run_evals
```

Offline mode is deterministic, free, and suitable for CI. It replays reviewed trajectory fixtures through the real graders. It validates the evaluation machinery; it does not prove that the current live model still produces those trajectories.

## Live evaluation

```bash
uv run python -m evals.run_evals --mode live
```

Live mode requires `OPENAI_API_KEY`, runs both real applications, and may incur provider charges. Results vary with model behavior and external weather availability. To run one implementation:

```bash
uv run python -m evals.run_evals --mode live --implementation no_framework
uv run python -m evals.run_evals --mode live --implementation openai_agents_sdk
```

Generated reports include final output, structured output, tool calls, handoffs, steps, latency, errors, checks, and aggregate scores. Token and cost fields are part of the schema but remain empty until adapters receive normalized usage data from each runtime.

## Adding a case

Add one JSON object per line to the golden dataset. Prefer behavioral requirements—required tools, forbidden claims, budgets, and status—over exact answer matching. Add or record a reviewed offline fixture, run the tests, and then run the offline evaluator.
