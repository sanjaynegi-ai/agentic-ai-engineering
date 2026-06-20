# Travel Planning Agent comparison

Both implementations answer the same request: "Plan a 2-day Jaipur trip for a family of 4 under ₹25,000. Check weather, estimate a basic budget, suggest an itinerary, and tell me whether to carry an umbrella."

They share conceptual tools—weather, safe arithmetic, current time, and local-notes search—and enforce travel scope, limits, and no live-booking claims. The no-framework version makes every loop boundary visible; the SDK version uses agents, tools, handoffs, structured output, guardrails, and tracing.

Both are evaluated with the same golden behavioral cases under `evals/`. Run `uv run python -m evals.run_evals` from the repository root for deterministic offline grading, or add `--mode live` to evaluate the real model-backed applications. See [the evaluation guide](../../evals/README.md).
