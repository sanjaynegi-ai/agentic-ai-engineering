# Agentic AI Engineering

This repo teaches agentic AI engineering by first building agents without a framework, then rebuilding similar systems with modern agent frameworks and SDKs such as OpenAI Agents SDK, CrewAI, LangGraph, Google ADK, and AutoGen. It also teaches the Model Context Protocol (MCP), an open protocol for connecting AI applications to external tools, resources, and reusable prompts.

The course joins three pillars: **first-principles agents**, **agent frameworks**, and **production AgentOps**.

- **Notebooks teach the concepts.**
- **Projects turn those concepts into working applications.**
- **Docs explain the engineering decisions and operationalize the systems.**

You do not need previous experience building AI agents. Basic Python knowledge is helpful, but the course introduces agent concepts before asking you to use a framework. It deliberately shows the machinery first—messages, structured outputs, tools, runtime loops, limits, and guardrails—so framework features do not feel like magic later.

## How to use this course

The repository uses the same three-part learning rhythm throughout:

1. **Learn in a notebook.** Read the explanation, run the small examples, and complete the exercise.
2. **Study and run a project.** See how the same idea is organized as a testable application with modules, prompts, configuration, and a UI.
3. **Use the docs as reference.** Return to `docs/` when you need a concise explanation or an operational command.

Start with the notebooks in numeric order. Do not try to understand every project folder on day one. The first useful milestone is to run the setup notebooks, understand the no-framework agent loop, and then compare it with the OpenAI Agents SDK implementation.

## Learning path

1. Set up Python 3.12, `uv`, environment variables, and Jupyter.
2. Build LLM calls, workflows, tool calling, guardrails, and an agent loop by hand.
3. Rebuild the same travel agent with OpenAI Agents SDK agents, tools, handoffs, structured output, guardrails, and tracing, then compare it with the no-framework implementation.
4. Explore CrewAI, LangGraph, Google ADK, and AutoGen, and learn how MCP connects agentic applications to external capabilities.
5. Test, observe, containerize, and deploy to Hugging Face Spaces, ECS Fargate, or EKS.

## Repository map

- `notebooks/` — guided lessons for setup, first principles, and SDK concepts.
- `projects/comparison_agent/` — two complete implementations of the same travel-planning scenario: one built from first principles and one built with OpenAI Agents SDK.
- `projects/no_framework_projects/` — the first implementation of each practice scenario, exposing runtime logic directly.
- `projects/openai_agents_sdk_projects/` — the same three practice scenarios rebuilt with OpenAI Agents SDK while preserving their input/output contracts.
- `projects/README.md` — the complete project lifecycle handbook: choose, run, test, evaluate, containerize, deploy with GitHub Actions/Terraform, observe, roll back, and clean up.
- `docs/` — concise concept, testing, Docker, and deployment references.
- `evals/` — shared golden cases and trajectory graders for comparing both travel agents.
- `prompts/` — reusable instructions kept separate from Python source code.
- `templates/`, `deployments/`, `.github/workflows/` — production and deployment starting points.

## Before you begin

Install the following on your computer:

- Python 3.12
- [`uv`](https://docs.astral.sh/uv/) for dependency and environment management
- Git, if you cloned the repository
- A code editor such as VS Code
- Docker Desktop only when you reach the container lessons

An OpenAI API key is required for live OpenAI model calls. You can still read the notebooks and run the deterministic tests without making paid API calls.

## Setup with uv

Run all setup commands from the repository root—the folder containing this README and `pyproject.toml`.

### 1. Create your private environment file

PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

This creates `.env` from the safe example file. Open `.env` and add your own `OPENAI_API_KEY` when you are ready for live model calls. The `.env` file is ignored by Git; never commit or share it.

### 2. Create the virtual environment and install dependencies

```bash
uv sync --group dev
```

`uv sync` reads `pyproject.toml` and `uv.lock`, creates `.venv` if necessary, and installs the exact course dependencies. The `--group dev` option also installs learning and quality tools such as Jupyter, pytest, and Ruff.

### 3. Register the course's Jupyter kernel

```bash
uv run python -m ipykernel install --user --name agentic-ai-engineering --display-name "Agentic AI Engineering"
```

This makes the repository's Python environment appear in Jupyter as **Agentic AI Engineering**. You normally need to register it only once. Select this kernel when opening a course notebook.

### 4. Start Jupyter Lab

```bash
uv run jupyter lab
```

This starts Jupyter Lab and normally opens it in your browser. Begin with `notebooks/00_setup/00_uv_jupyter_setup.ipynb`, then continue in numeric order. Keep this terminal running while Jupyter is open; press `Ctrl+C` in the terminal to stop it.

## Project lifecycle: start here

The root README is the entry point; [`projects/README.md`](projects/README.md) is the detailed operating manual. Use the same lifecycle for the no-framework and OpenAI Agents SDK implementations today and for future LangGraph, Google ADK, CrewAI, or AutoGen implementations.

1. **Choose a matched scenario** from [`projects/project_catalog.json`](projects/project_catalog.json). Study the no-framework version first, then the SDK version.
2. **Run locally** from the repository environment:

   ```bash
   uv run python projects/no_framework_projects/customer_support_router/app.py
   ```

3. **Validate behavior and quality**:

   ```bash
   make project-check
   ```

4. **Build and exercise the exact Docker context**:

   ```bash
   docker build -t customer-support-router:local projects/no_framework_projects/customer_support_router
   docker run --rm --env-file projects/no_framework_projects/customer_support_router/.env -p 7860:7860 customer-support-router:local
   ```

5. **Publish or deploy from GitHub Actions**. The manual workflows resolve the selected scenario/framework, authenticate to AWS through OIDC, create ECR and application infrastructure with Terraform, and reuse immutable commit-tagged images.
6. **Observe and operate**. Follow local logs and container statistics, inspect CloudWatch logs/dashboards/alarms for ECS or pod logs/events/metrics for EKS, and correlate failures with agent traces and evaluations.
7. **Undeploy to stop charges**. Run **Terraform undeploy project from AWS**, retype the exact selector, and let Terraform destroy project-owned ECS/EKS resources before deleting ECR images and the repository. Shared infrastructure and S3 state history remain intact.

Before executing steps 4–6, read the complete [project build, AWS deployment, credential, observability, rollback, and cleanup handbook](projects/README.md). The concise AWS checklist is in [`docs/project_to_aws.md`](docs/project_to_aws.md), while [`infra/terraform/`](infra/terraform/) is the deployment source of truth.

## Run the comparison projects

The comparison folder contains **two separate applications** that solve the same travel-planning problem. They are not two steps of one program, and you do not need to run their commands in sequence.

Run one implementation, explore it, stop it with `Ctrl+C`, and then run the other when you are ready to compare them. Both use port `7860` by default, so running one at a time also avoids a port conflict.

### Option A: No-framework travel agent

```bash
uv run python projects/comparison_agent/no_framework/app.py
```

Choose this version first. It implements the agent loop directly in Python so you can inspect message construction, tool requests, validation, tool execution, stopping conditions, memory, and observability. When it starts, open the local Gradio URL printed in the terminal.

Read its [project guide](projects/comparison_agent/no_framework/README.md) before changing the code.

### Option B: OpenAI Agents SDK travel team

```bash
uv run python projects/comparison_agent/openai_agents_sdk/app.py
```

This is a different project that rebuilds the travel scenario with SDK concepts such as `Agent`, `Runner`, function tools, handoffs, guardrails, structured output, sessions, and tracing. Run it after studying the no-framework version so you can identify which responsibilities the SDK abstracts.

Read its [project guide](projects/comparison_agent/openai_agents_sdk/README.md) for the architecture and limitations.

## Run quality checks

Quality checks do not start either application. They inspect the repository and then exit. You may run them independently in any order, although the order below is a useful workflow after making changes.

### 1. Run the automated tests

```bash
uv run pytest
```

`pytest` checks deterministic behavior such as schema validation, guardrails, safe calculation, tool registration, agent stopping limits, and project service functions. These tests do not make live paid model calls.

### 2. Check Python code quality

```bash
uv run ruff check .
```

Ruff scans the Python source for problems such as undefined names, suspicious constructs, and selected correctness issues. It is a fast static check: it examines code without launching the apps.

### 3. Validate the course structure and notebooks

```bash
uv run python scripts/validate_repo.py
```

`validate_repo.py` performs repository-specific checks that pytest and Ruff do not cover. It verifies that required learning files exist and that all course notebooks are real, valid notebook documents with the expected cells and metadata.

For a final local check, run all three commands. A passing result means the deterministic tests, selected code-quality rules, and course structure are healthy; it does not guarantee that a live provider API or Docker daemon is available.

### 4. Evaluate agent behavior

```bash
uv run python -m evals.run_evals
```

This runs shared golden behavioral cases against reviewed offline trajectories for both comparison agents. Unlike unit tests, the evals grade final behavior, required and forbidden tools, tool-call limits, safety refusals, prohibited claims, and budget constraints. See [Evaluating agentic AI systems](docs/evals_and_tests.md) and the [evaluation harness guide](evals/README.md).

## Run with Docker

Docker is optional for the early lessons. Start Docker Desktop before running these commands. For example, to build and run the no-framework comparison project:

```bash
docker build -t comparison-no-framework projects/comparison_agent/no_framework
docker run --env-file .env -p 7860:7860 comparison-no-framework
```

The root Compose file also defines both comparison applications as separate profiles. See [Docker Compose](docs/docker_compose.md) and the individual project READMEs before using those profiles.

## Suggested first study session

If you are completely new, use this sequence:

1. Complete the four setup steps above.
2. Open and run both notebooks in `notebooks/00_setup/`.
3. Work through `notebooks/01_first_principles/01_basic_llm_calls.ipynb`.
4. Continue through the first-principles notebooks in numeric order.
5. Run the no-framework comparison project.
6. Run pytest, Ruff, the repository validator, and the offline agent evaluation.
7. Move to `notebooks/02_openai_agents_sdk/` and then run the SDK comparison project.

It is fine to pause before Docker and deployment. Those topics make more sense after the local agent architecture is familiar.

## Deployment paths

- **Hugging Face Spaces** for approachable Gradio demos.
- **AWS ECS Fargate** for managed container orchestration without managing nodes.
- **AWS EKS** when Kubernetes portability and platform controls justify the complexity.

Every project follows one reusable delivery contract: runnable Python application, deterministic tests and evaluation, locked dependencies, non-root Docker image, private ECR repository, and Terraform-managed application infrastructure. The same contract applies when the course adds LangGraph, Google ADK, CrewAI, AutoGen, or another framework; only the project implementation and catalog entry should change.

AWS deployment workflows are manual (`workflow_dispatch`) and use a protected GitHub `production` environment. GitHub exchanges an OIDC token for short-lived AWS credentials, Terraform state lives in an encrypted/versioned S3 bucket with state locking, the OpenAI key lives in AWS Secrets Manager, and images are pushed to private ECR repositories with immutable tags and scan-on-push enabled. Do not store long-lived AWS keys, API keys, `.env`, or Terraform state in GitHub or the repository.

The workflows validate the selected implementation, create/reconcile ECR through Terraform, build the exact project context, push a commit-SHA image, optionally deploy it to ECS Fargate or an existing EKS cluster, and safely undeploy project-owned resources afterward. Start with the complete [project lifecycle handbook](projects/README.md), read [AWS services, Terraform state, and project cleanup](docs/aws_services_and_cleanup.md), use [From project idea to AWS deployment](docs/project_to_aws.md) as the concise operational checklist, and treat [`infra/terraform/`](infra/terraform/) as the infrastructure source of truth.

## Framework comparison

| Approach | Control | Built-in orchestration | Best learning use |
|---|---:|---:|---|
| No framework | Highest | None | Understand the runtime loop |
| OpenAI Agents SDK | High | Tools, handoffs, guardrails, tracing | Production OpenAI agent apps |
| CrewAI | Medium | Roles, tasks, crews, flows | Role-oriented collaboration |
| LangGraph | High | Graph state and persistence | Explicit stateful workflows |
| Google ADK | Medium | Code-first agents and evaluation | Google ecosystem projects |
| AutoGen | Medium | AgentChat and teams | Conversation-oriented multi-agent systems |
| MCP | Protocol | Tool/resource/prompt interoperability | Connecting models to capabilities |

## Security and cost

Treat model output and tool arguments as untrusted input. Protect API keys, validate every tool call, use allowlists and step/token limits, and configure provider spend limits before live exercises. Never expose a Gradio share link with privileged tools.

## Where to get more context

- Use the [documentation index](docs/README.md) when you need a concept or operations reference.
- Read the [comparison project overview](projects/comparison_agent/README.md) before comparing implementations.
- Follow the [observability standard](docs/observability.md) for logs, traces, metrics, evaluations, alerts, and incident handling.
- Use the [AWS services and cleanup guide](docs/aws_services_and_cleanup.md) before destroying project infrastructure.
- Use the [framework selection guide](docs/framework_selection_guide.md) after you understand the first-principles loop.
- Read each project's own README before running or modifying that project.

When something fails, read the full terminal error first. Confirm that you are in the repository root, that `uv sync --group dev` completed, that the correct Jupyter kernel is selected, and that `.env` contains the required key for live examples.
