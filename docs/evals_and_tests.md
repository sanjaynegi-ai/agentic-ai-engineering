# Evaluating agentic AI systems

Agent evaluation asks two questions:

1. Did the system produce an acceptable result?
2. Did it take an acceptable path to produce that result?

Traditional unit tests remain essential for schemas, tools, registries, guardrails, and stopping conditions. They are necessary but insufficient because model decisions and multi-step trajectories are probabilistic. Agent projects also need versioned evaluation cases that describe acceptable behavior.

## How agent evaluation differs from RAG evaluation

A RAG evaluation commonly measures retrieval relevance, context precision and recall, answer groundedness, citation correctness, and final-answer quality. Its golden dataset may identify the expected source documents, facts, citations, or reference answer.

An agent can retrieve information, choose tools, mutate state, delegate to specialists, repeat actions, stop early, or trigger side effects. Its evaluation therefore extends the RAG-style final-answer checks with runtime behavior:

| Evaluation layer | RAG example | Agent example |
|---|---|---|
| Evidence | Were the correct passages retrieved? | Did the agent select the correct evidence tool? |
| Grounding | Is the answer supported by retrieved context? | Is the answer supported by every relevant tool result? |
| Final result | Is the answer correct and relevant? | Did the agent complete the goal within stated constraints? |
| Tool choice | Usually part of the retrieval pipeline | Were required tools used and forbidden tools avoided? |
| Arguments | Was the retrieval query useful? | Were city, dates, amounts, and permissions passed correctly? |
| Trajectory | Usually a fixed pipeline | Were steps, retries, handoffs, and loops reasonable? |
| Safety | Did the answer avoid unsupported claims? | Did guardrails stop unsafe actions and unauthorized side effects? |
| Operations | Retrieval and generation latency/cost | Total turns, tools, tokens, latency, cost, errors, and side effects |

The key difference is that an agent's **trajectory is part of the product behavior**. Two agents can return similar prose while one used the wrong tool, exceeded its budget, ignored a guardrail, or claimed an action it never performed.

## Golden datasets for agents

Golden agent cases should define behavior rather than one exact paragraph. Useful fields include:

- Input and category
- Expected completion or refusal
- Required and forbidden tools
- Argument constraints
- Required or forbidden handoffs
- Required answer facts or terms
- Forbidden claims and side effects
- Maximum tool calls or turns
- Budget and latency thresholds
- Expected citations or trusted evidence

Prefer deterministic graders for facts that code can check. Use an optional model-based judge only for subjective qualities such as clarity, usefulness, or tone. Keep model judges rubric-driven, sample their disagreements, and never let a single judge score hide hard safety failures.

## Evaluation layers used in this repository

The shared harness under `evals/` supports:

1. **Unit tests** for deterministic modules and boundaries.
2. **Golden behavioral cases** shared by both travel-agent implementations.
3. **Trajectory checks** for tools, tool budgets, handoffs, and stopping behavior.
4. **Safety checks** for expected refusals, forbidden tools, and prohibited claims.
5. **Structured-result checks** such as the user's maximum travel budget.
6. **Operational fields** for latency, steps, tokens, cost, and errors.

Run the deterministic offline evaluation with:

```bash
uv run python -m evals.run_evals
```

Offline fixtures make the grading logic reproducible and free in CI. They do not replace live evaluation. Run both real agents with an API key using:

```bash
uv run python -m evals.run_evals --mode live
```

Live results are written to `evals/reports/`, which is intentionally ignored by Git. Review failures case by case rather than trusting only the aggregate score.

## What to track over time

Track task success, refusal quality, tool and handoff accuracy, groundedness, citation validity, loop rate, latency, token use, estimated cost, errors, and side-effect safety. Add adversarial cases for prompt injection, unsafe requests, malformed tools, unavailable services, and attempts to exceed scope.
