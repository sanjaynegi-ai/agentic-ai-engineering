# Customer Support Router

## Learning objective
Implement deterministic routing, confidence, human escalation, and a draft-only response. This is the first-principles half of the pair; rebuild the same contract in [`openai_agents_sdk_projects/customer_support_router`](../../openai_agents_sdk_projects/customer_support_router).

## Architecture
`app.py` → typed `service.run()` → domain rules/tools → Pydantic result. Reusable instructions live in `prompts/`; sample trusted data lives in `data/`. SDK projects additionally expose `build_agent()` and opt-in `run_live()`.

## Run locally
From this project directory: copy `.env.example` to `.env`, run `uv sync --group dev`, then `uv run python app.py`. Open `http://localhost:7860`. Stop with `Ctrl+C`.

## Tests and evaluation
Run `uv run pytest`. From the repository root run `uv run python -m evals.run_project_evals --project customer_support_router`. Offline paths require no API key.

## Docker
`docker build -t customer_support_router:local .` then `docker run --env-file .env -p 7860:7860 customer_support_router:local`.

## AWS deployment
Follow [the project-to-AWS guide](../../../docs/project_to_aws.md). Select `customer_support_router` when dispatching the ECR, ECS Fargate, or EKS workflow.

## Environment and safety
`OPENAI_API_KEY` is required only for live SDK/model calls. Never commit `.env`. The baseline does not execute bookings, send support replies, access email/calendar, or mutate external systems.

## Exercises
Add a golden case, make it pass, add an observable event, run the container, then deploy the immutable image tag through GitHub Actions.
