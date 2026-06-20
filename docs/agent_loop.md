# Agent loop

An AI agent is a program where an LLM is given a goal, context, and available actions, and the LLM's outputs help decide the next step of execution. The surrounding runtime manages state, validates tool calls, executes tools, enforces guardrails, tracks costs, and decides when to stop.

`observe -> decide -> act -> observe result -> continue or finish`

Stop on a final answer, maximum steps, maximum tool calls, a repeated tool call, invalid tool call, exceeded budget, or required human approval. Every stop should produce an explicit event and a safe user-facing result.
