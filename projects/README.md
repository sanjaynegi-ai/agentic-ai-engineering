# Projects: build, run, package, and deploy

This directory is the application layer of the course. Notebooks explain individual concepts; each project turns those concepts into a runnable service with tests, an offline evaluation path, a Gradio UI, a reproducible Docker image, and an AWS deployment path.

The learning rule is deliberate: study the no-framework implementation first, then run the **same scenario and output contract** through OpenAI Agents SDK. Future framework implementations such as LangGraph, Google ADK, CrewAI, or AutoGen should follow the same project contract and delivery process described here.

## Project catalog

| Scenario | First: no framework | Then: OpenAI Agents SDK | Deployment selector |
|---|---|---|---|
| Flagship travel agent | [`comparison_agent/no_framework`](comparison_agent/no_framework) | [`comparison_agent/openai_agents_sdk`](comparison_agent/openai_agents_sdk) | `comparison_travel_agent_<implementation>` |
| Travel planner | [`no_framework_projects/travel_planner_agent`](no_framework_projects/travel_planner_agent) | [`openai_agents_sdk_projects/travel_planner_agent`](openai_agents_sdk_projects/travel_planner_agent) | `travel_planner_agent_<implementation>` |
| Support router | [`no_framework_projects/customer_support_router`](no_framework_projects/customer_support_router) | [`openai_agents_sdk_projects/customer_support_router`](openai_agents_sdk_projects/customer_support_router) | `customer_support_router_<implementation>` |
| Research assistant | [`no_framework_projects/research_assistant_agent`](no_framework_projects/research_assistant_agent) | [`openai_agents_sdk_projects/research_assistant_agent`](openai_agents_sdk_projects/research_assistant_agent) | `research_assistant_agent_<implementation>` |

`<implementation>` is `no_framework` or `openai_agents_sdk`. The machine-readable source of paths, ports, and evaluator types is [`project_catalog.json`](project_catalog.json). GitHub Actions resolves its selector through [`scripts/resolve_project.py`](../scripts/resolve_project.py), so project paths are not duplicated in deployment scripts.

## What a complete project contains

Every deployable project context contains:

| File or directory | Responsibility |
|---|---|
| `README.md` | Scenario-specific behavior, architecture, limits, and commands |
| `app.py` | Gradio entry point listening on `0.0.0.0:7860` |
| `src/<package>/` | Typed application and agent logic |
| `prompts/` | Version-controlled model instructions |
| `data/` | Small trusted local fixtures or evidence |
| `tests/` | Deterministic unit and contract tests |
| `.env.example` | Safe variable names with no real credentials |
| `pyproject.toml` and `uv.lock` | Dependencies and reproducible resolution |
| `Dockerfile` | Linux production image running as a non-root user |
| `.dockerignore` | Prevents secrets, caches, tests, and local environments entering the build context |
| `docker-compose.yml` | Convenient local container run configuration |

The application must bind to port `7860`, fail clearly on invalid input, expose an offline path that does not require paid API calls, and keep side effects bounded. A support project drafts a response; it does not send one. A travel project proposes an itinerary; it does not book one.

## The complete delivery flow

```text
project code -> unit tests -> shared eval -> Docker build -> ECR image
                                                        |
                                                        +-> ECS Fargate + ALB
                                                        |
                                                        +-> existing EKS cluster

GitHub Actions: validates and orchestrates
Terraform:      owns AWS/ECS/EKS application resources
S3:             stores encrypted, locked Terraform state
Secrets Manager: stores the OpenAI API key
GitHub OIDC:    supplies short-lived AWS credentials
```

## 1. Local prerequisites

Install Python 3.12, `uv`, Git, and Docker Desktop. Terraform 1.10 or newer is needed when validating infrastructure locally because the workflows use native S3 lockfiles; AWS CLI and `kubectl` are needed only for manual AWS/EKS inspection.

From the repository root:

```bash
uv sync --frozen --group dev
uv run pytest
uv run python scripts/validate_repo.py
```

Use `--frozen` in CI and verification so a stale lockfile fails instead of silently changing dependencies.

## 2. Configure local environment variables

Copy the selected project's example file to `.env`. PowerShell example:

```powershell
$project = "projects/no_framework_projects/customer_support_router"
Copy-Item "$project/.env.example" "$project/.env"
```

macOS/Linux:

```bash
project=projects/no_framework_projects/customer_support_router
cp "$project/.env.example" "$project/.env"
```

Offline `run()` paths and deterministic tests do not require a key. Add `OPENAI_API_KEY` only for a live model path. `.env` and `.env.*` are ignored by Git; `.env.example` is the only environment file that belongs in source control.

Never put an AWS access key, OpenAI API key, `.env`, private key, or Terraform state file in the repository or Docker image.

## 3. Run a project in development

There are two supported workflows.

### Use the repository environment

Run from the repository root after `uv sync --frozen --group dev`:

```bash
uv run python projects/no_framework_projects/customer_support_router/app.py
```

Open `http://localhost:7860`. Stop the server with `Ctrl+C`.

### Use the project's isolated environment

Run from the project directory when developing or deploying that project independently:

```bash
cd projects/no_framework_projects/customer_support_router
uv sync --frozen --group dev
uv run pytest
uv run python app.py
```

This uses the project's own `pyproject.toml` and `uv.lock`, which is also what the Docker build uses.

## 4. Test and evaluate before packaging

From the repository root, run the complete deterministic gate:

```bash
uv run pytest
uv run ruff check .
uv run python scripts/validate_repo.py
uv run python -m evals.run_project_evals --project customer_support_router
uv run python -m evals.run_evals
```

`run_project_evals` runs both implementations by default. Isolate one side with:

```bash
uv run python -m evals.run_project_evals \
  --project customer_support_router \
  --implementation openai_agents_sdk
```

The flagship comparison uses `evals.run_evals`. GitHub Actions selects the correct evaluator from `project_catalog.json`.

## 5. Build and test a Docker image locally

Start Docker Desktop and confirm both client and server are available:

```bash
docker version
```

Build from the repository root. The build context must be the selected project directory:

```bash
docker build \
  --tag customer-support-router:no-framework-local \
  projects/no_framework_projects/customer_support_router
```

Run the image with the local environment file mounted as environment variables, not copied into the image:

```bash
docker run --rm \
  --env-file projects/no_framework_projects/customer_support_router/.env \
  --publish 7860:7860 \
  customer-support-router:no-framework-local
```

PowerShell accepts the same command on one line. Open `http://localhost:7860`, inspect `docker logs <container>`, then stop it with `Ctrl+C`.

Alternatively, from the project directory:

```bash
docker compose up --build
docker compose down
```

The Dockerfiles install the exact locked runtime dependencies, copy only runtime files, run as UID `10001`, and never copy `.env`. GitHub builds `linux/amd64` images because ECS and the example EKS path assume x86_64 worker capacity.

Useful verification commands:

```bash
docker image inspect customer-support-router:no-framework-local
docker history customer-support-router:no-framework-local
docker run --rm customer-support-router:no-framework-local id
```

The final command should show a non-root user.

## 6. AWS architecture and ownership

The repository separates application artifacts from deployment control:

- **Amazon ECR** stores one private repository per scenario/framework selector. Tags are immutable, images are scanned on push, AES-256 encryption is enabled, and lifecycle policy retains the newest 30 images.
- **Amazon S3** stores Terraform state. The bucket must be private, encrypted, versioned, and restricted to the deployment role. Workflows enable native S3 state locking with `use_lockfile=true`.
- **AWS Secrets Manager** stores the OpenAI API key as the secret's plaintext value. The repository stores only its ARN as `OPENAI_SECRET_ARN`.
- **ECS Fargate** runs one isolated cluster/service, task definition, log group, security groups, and Application Load Balancer per deployment selector.
- **EKS** is optional and assumes an existing cluster. Terraform owns the project Deployment and Service. The workflow creates the shared namespace and Kubernetes Secret before `terraform apply`, keeping the API key out of Terraform state.
- **GitHub Actions** authenticates through OIDC. Do not create `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` GitHub secrets.

The ECS example exposes HTTP on port 80 for teaching simplicity. A production internet service should add an ACM certificate, HTTPS listener, DNS, WAF/rate limiting where appropriate, private application subnets, and tighter egress.

## 7. Bootstrap AWS once

These account-level prerequisites are intentionally not auto-created by an application workflow:

1. An AWS account and target region.
2. A private S3 Terraform-state bucket with default encryption and versioning.
3. A GitHub OIDC provider for `token.actions.githubusercontent.com`.
4. An IAM deployment role trusted only by the intended repository, branch/environment, and GitHub audience `sts.amazonaws.com`.
5. Least-privilege permissions for the Terraform resources being managed, ECR push, state-bucket access, and `secretsmanager:GetSecretValue`.
6. A Secrets Manager secret whose plaintext value is the OpenAI API key.
7. For ECS: an existing VPC and at least two public subnets in different Availability Zones for the example ALB/Fargate layout.
8. For EKS: an existing cluster, worker capacity, an EKS access entry for the deployment role, and permission to create namespace/deployment/service/secret resources.

Example secret creation—run locally, never paste the key into a committed script:

```bash
aws secretsmanager create-secret \
  --name agentic-ai/openai-api-key \
  --secret-string "$OPENAI_API_KEY"
```

Record the returned ARN. Rotate the value in Secrets Manager without changing source code.

## 8. Configure the GitHub `production` environment

Create a protected GitHub Environment named `production`. Require reviewers for deployments when the repository is used by a team.

Configure these **environment variables** (not source files):

| Variable | Used by | Example/meaning |
|---|---|---|
| `AWS_DEPLOY_ROLE_ARN` | all AWS workflows | ARN of the GitHub OIDC role |
| `AWS_REGION` | all AWS workflows | `ap-south-1` |
| `TF_STATE_BUCKET` | Terraform | Existing private state bucket name |
| `OPENAI_SECRET_ARN` | ECS and EKS | Secrets Manager ARN; the key value remains in AWS |
| `AWS_VPC_ID` | ECS | Existing VPC ID |
| `AWS_PUBLIC_SUBNET_IDS_JSON` | ECS | JSON list such as `["subnet-a","subnet-b"]` |
| `EKS_CLUSTER` | EKS | Existing cluster name |

The ARN values identify resources and normally do not need secret masking. The actual OpenAI key belongs only in Secrets Manager. If your organization classifies account identifiers as confidential, store the ARNs as GitHub environment secrets and update the workflow references consistently.

## 9. GitHub Actions workflows

| Workflow | Purpose | AWS mutation |
|---|---|---|
| `test.yml` / `lint.yml` | CI checks | None |
| `build-docker.yml` | Generic comparison-image build check | None |
| `build-push-ecr.yml` | Test, evaluate, create ECR through Terraform, and push an immutable image | ECR and state |
| `deploy-ecs-manual.yml` | Test, evaluate, build/push, then apply the ECS stack | ECR, ECS, ALB, IAM, logs |
| `deploy-eks-manual.yml` | Test, evaluate, build/push, create runtime secret, then apply the EKS app stack | ECR and EKS app resources |
| `undeploy-aws-project.yml` | Destroy all Terraform-owned resources for one selector in safe order | Removes ECS/EKS app stacks and ECR |

AWS workflows are manual (`workflow_dispatch`) and run in the protected `production` environment. Each defaults the image tag to the commit SHA. Supplying a tag is optional, but it must be Docker-compatible and must not already exist because ECR tags are immutable.

Each workflow follows this order:

1. Check out the exact commit.
2. Install `uv` and sync the frozen root lockfile.
3. Run unit tests and the selected implementation's evaluator.
4. Resolve the selector through `project_catalog.json` and produce a DNS-safe deployment name.
5. Exchange the GitHub OIDC token for short-lived AWS credentials.
6. Initialize encrypted, locked remote Terraform state and validate the stack.
7. Create or reconcile ECR; reuse the immutable tag if it already exists, otherwise build and push the Linux image.
8. For deployment workflows, apply ECS or EKS resources and publish outputs to the job summary.

## 10. Terraform structure

```text
infra/terraform/
|-- ecr/       one private, immutable, scanned repository per selector
|-- ecs/       Fargate cluster/service, IAM, logs, ALB, target group, networking
|-- eks/       Deployment and LoadBalancer Service in an existing cluster
`-- README.md  stack ownership and local validation
```

Every selector has separate state keys:

```text
ecr/<selector>.tfstate
ecs/<selector>.tfstate
eks/<selector>.tfstate
```

This prevents one project/framework deployment from overwriting another. Do not commit `.terraform/`, plans containing sensitive values, or `*.tfstate` files.

Validate infrastructure locally without applying:

```bash
terraform fmt -check -recursive infra/terraform
terraform -chdir=infra/terraform/ecr init -backend=false
terraform -chdir=infra/terraform/ecr validate
terraform -chdir=infra/terraform/ecs init -backend=false
terraform -chdir=infra/terraform/ecs validate
terraform -chdir=infra/terraform/eks init -backend=false
terraform -chdir=infra/terraform/eks validate
```

## 11. Deploy, verify, roll back, and clean up

### Build and push only

Open **Actions → Terraform ECR and push project image → Run workflow**, select a project/framework selector, and normally leave `image_tag` blank. Confirm the job summary contains the full ECR image URI.

### Deploy to ECS Fargate

Run **Terraform deploy project to ECS Fargate**. After completion:

- Open the Application URL from the job summary.
- Check the ECS service reached a steady state.
- Check target health and CloudWatch logs under `/ecs/agentic-ai/...`.
- Confirm the task definition references an immutable ECR tag and a Secrets Manager ARN.

Roll back by dispatching the workflow from a known-good commit or with a known-good immutable tag. The deploy workflows check ECR first, so an image created by the ECR-only workflow is reused rather than rebuilt; this gives the repository a build-once/promote-the-same-artifact path.

### Deploy to EKS

Run **Terraform deploy project to EKS**, then inspect:

```bash
kubectl --namespace agentic-ai get deployments,pods,services
kubectl --namespace agentic-ai rollout status deployment/<dns-safe-selector>
kubectl --namespace agentic-ai logs deployment/<dns-safe-selector>
```

Roll back with `kubectl rollout undo` or rerun Terraform with a previous immutable image. The example workflow refreshes the Kubernetes Secret from Secrets Manager on every deployment.

### Cleanup

AWS resources cost money even when nobody is using the course app. Use **Actions → Terraform undeploy project from AWS** as soon as the exercise is complete:

1. Select the deployed scenario/framework selector.
2. Retype that exact value in `confirm_project`.
3. Approve the protected `production` environment if required.
4. Let the workflow destroy ECS, then EKS application resources, then ECR and its images.
5. Review the summary and verify that billable project resources are gone.

The cleanup workflow inspects the authoritative S3 state objects and skips missing or already-empty stacks. It saves and applies explicit destroy plans, checks that each resulting state is empty, and stops before ECR deletion if application teardown fails. Build, deploy, and undeploy workflows share one selector-level concurrency group, preventing overlapping Terraform operations.

The workflow preserves the remote state bucket and history, OIDC role, VPC/subnets, EKS cluster, shared Kubernetes namespace/secret, Secrets Manager secret, DNS/certificates, budgets, and audit infrastructure. Those are shared or externally managed resources. See [AWS services, Terraform state, and project cleanup](../docs/aws_services_and_cleanup.md) for service ownership, state best practices, permissions, cost drivers, verification commands, and failure recovery.

## 12. Observe and operate the project

Observability is part of the project lifecycle, not a post-deployment extra. Use four complementary signals:

| Signal | Question it answers | Repository/AWS source |
|---|---|---|
| Logs | What happened during this request or process? | Console, `docker logs`, CloudWatch Logs, `kubectl logs` |
| Traces | Which model, tool, handoff, or guardrail step caused it? | Comparison-project events and OpenAI Agents SDK tracing |
| Metrics/alarms | Is the service healthy in aggregate? | Docker stats, ECS/ALB metrics, Container Insights, Kubernetes metrics |
| Evaluations | Is agent behavior still correct and safe? | `evals.run_evals` and `evals.run_project_evals` |

### Local and Docker observability

Set `LOG_LEVEL=INFO` in the local `.env`, run the project, and keep the terminal visible. Never log API keys, full authorization headers, raw personal data, or unredacted prompt/tool payloads.

For a container:

```bash
docker ps
docker logs --follow <container-name>
docker stats <container-name>
docker inspect <container-name> --format '{{json .State}}'
```

When diagnosing an agent failure, capture the request/correlation ID, implementation, prompt version, model, validated tool names and latency, guardrail outcome, turn/tool limits, token usage, final status, and exception type. Keep raw user content redacted or sampled separately with restricted access. The flagship comparison projects demonstrate event recording; future framework projects must emit equivalent structured events to standard output so the deployment platform can collect them.

### ECS and CloudWatch observability

The ECS Terraform stack enables Container Insights and creates:

- A 14-day CloudWatch log group under `/ecs/agentic-ai/...`
- CPU and memory alarms at 80% for ten minutes
- An unhealthy-target alarm for the Application Load Balancer
- A CloudWatch dashboard for CPU, memory, target latency, target 5xx responses, unhealthy hosts, and recent error logs

The ECS workflow writes the application URL, cluster, service, log group, dashboard, and target group to the GitHub job summary. Use those outputs with:

```bash
aws logs tail <cloudwatch-log-group> --follow --since 30m
aws ecs describe-services --cluster <ecs-cluster> --services <ecs-service>
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
aws cloudwatch get-dashboard --dashboard-name <dashboard-name>
aws cloudwatch describe-alarms --alarm-name-prefix <deployment-name>
```

The baseline alarms have no notification action because the course cannot guess a team's incident channel. In a real environment, attach an SNS topic, route it to email/PagerDuty/Slack through your approved integration, and test the notification path.

### EKS observability

The EKS application stack provides liveness/readiness probes and resource requests/limits. Inspect runtime state with:

```bash
kubectl --namespace agentic-ai get deployments,pods,services
kubectl --namespace agentic-ai rollout status deployment/<dns-safe-selector>
kubectl --namespace agentic-ai logs deployment/<dns-safe-selector> --all-pods=true --follow
kubectl --namespace agentic-ai get events --sort-by=.lastTimestamp
kubectl --namespace agentic-ai top pods
kubectl --namespace agentic-ai describe deployment/<dns-safe-selector>
```

`kubectl top` requires Metrics Server. Centralized EKS logs and infrastructure metrics require a platform-level collector such as CloudWatch Container Insights/OpenTelemetry, which this application stack intentionally does not install. The cluster owner should configure that once for the cluster rather than every project installing a competing agent.

### Agent traces and quality monitoring

For live OpenAI Agents SDK runs, use SDK tracing to inspect agent spans, tool calls, handoffs, guardrails, and errors. Keep sensitive-data tracing disabled unless the data classification and retention policy explicitly allow it. A trace explains one run; it does not replace aggregate service metrics or behavioral evaluations.

Run offline evaluations before deployment and after changing prompts, tools, models, guardrails, or framework versions:

```bash
uv run python -m evals.run_project_evals
uv run python -m evals.run_evals
```

For production monitoring, track at minimum:

- Request success/error rate and p50/p95 latency
- Healthy task/pod count, restarts, CPU, memory, and ALB target health
- Model/tool latency, token usage, estimated cost, and rate-limit failures
- Guardrail refusals, human-escalation rate, tool-call limit exhaustion, and handoff failures
- Evaluation pass rate for safety, scope, required tools, and final-answer quality

### Incident and rollback loop

1. Confirm endpoint and target/pod health.
2. Find the failing request by timestamp and correlation ID.
3. Inspect application logs and the agent trace without exposing secrets.
4. Compare the deployed image tag, prompt/model configuration, and latest evaluation result.
5. Roll back to a known-good immutable image or undo the Kubernetes rollout.
6. Re-run the failing case as a deterministic regression evaluation.
7. Record the cause, remediation, and whether an alarm or evaluator should have detected it earlier.

See [`docs/observability.md`](../docs/observability.md) for the signal and data-handling standard.

## 13. Adding LangGraph, Google ADK, or another framework

Use the same process rather than inventing a parallel deployment path:

1. Add `projects/<framework>_projects/<scenario>/` with the complete project file contract above.
2. Preserve the scenario's input/output behavior so evaluations remain comparable.
3. Add the new implementation and context to `project_catalog.json`.
4. Add its selector to the three manual workflow choice lists.
5. Extend the evaluator only when the existing evaluator cannot execute the framework's offline path.
6. Generate and commit the project `uv.lock`.
7. Run tests, project evals, Docker build/run, Compose validation, workflow YAML parsing, and Terraform validation.
8. Emit structured, redacted lifecycle events and preserve correlation IDs across agents, tools, and handoffs.
9. Reuse ECR, ECS, EKS, OIDC, state, secret, dashboard, alarm, and rollback conventions unchanged.

Framework code changes; the production delivery contract does not.

## Verification boundary

Local tests, evals, Dockerfile/Compose validation, workflow parsing, and `terraform validate` can run without an AWS account. A successful real deployment additionally depends on account-specific IAM, S3, VPC/subnet, Secrets Manager, ECR, ECS/EKS, quotas, and billing configuration. Never describe an AWS deployment as verified until the workflow has run in the target account and the application endpoint has been exercised.
