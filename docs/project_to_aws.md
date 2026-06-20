# From project idea to AWS deployment

The canonical, detailed handbook is [`projects/README.md`](../projects/README.md). This page is the shorter operational checklist.

## Local gate

From the repository root:

```bash
uv sync --frozen --group dev
uv run pytest
uv run ruff check .
uv run python scripts/validate_repo.py
uv run python -m evals.run_project_evals --project customer_support_router
```

Build and run the exact project context:

```bash
docker build -t customer-support-router:local projects/no_framework_projects/customer_support_router
docker run --rm --env-file projects/no_framework_projects/customer_support_router/.env -p 7860:7860 customer-support-router:local
```

## AWS and GitHub prerequisites

- Private, encrypted, versioned S3 bucket for Terraform state
- GitHub OIDC provider and least-privilege deployment role; no stored AWS access keys
- OpenAI API key stored as plaintext secret value in AWS Secrets Manager
- Protected GitHub environment named `production`
- Environment variables: `AWS_DEPLOY_ROLE_ARN`, `AWS_REGION`, `TF_STATE_BUCKET`, `OPENAI_SECRET_ARN`
- ECS variables: `AWS_VPC_ID`, `AWS_PUBLIC_SUBNET_IDS_JSON`
- EKS variable: `EKS_CLUSTER`, plus an existing cluster and access entry for the deployment role

Workflows enable S3 encryption and native lockfiles. ECS tasks read the API key directly from Secrets Manager. The EKS workflow refreshes a Kubernetes Secret from Secrets Manager before Terraform applies the Deployment and Service, so the key is not written into Terraform state.

## Deployment workflows

1. **Terraform ECR and push project image** tests/evaluates the selector, creates an immutable/scanned ECR repository, and makes a commit-SHA image available.
2. **Terraform deploy project to ECS Fargate** performs the same build and creates an isolated Fargate service, IAM roles, CloudWatch logs, security groups, ALB, and target group.
3. **Terraform deploy project to EKS** reuses the same image when already present (or builds it when absent), creates the runtime secret outside Terraform state, and applies app resources to an existing cluster.
4. **Terraform undeploy project from AWS** destroys non-empty ECS and EKS application states before force-deleting the project's ECR repository and images.

The selector combines scenario and implementation, for example `customer_support_router_openai_agents_sdk`. [`scripts/resolve_project.py`](../scripts/resolve_project.py) resolves it through [`projects/project_catalog.json`](../projects/project_catalog.json) and creates an AWS/Kubernetes-safe deployment name.

## Infrastructure ownership

- `infra/terraform/ecr`: one ECR repository per selector
- `infra/terraform/ecs`: per-selector ECS application stack
- `infra/terraform/eks`: per-selector Deployment and LoadBalancer Service
- S3 keys: `ecr/<selector>.tfstate`, `ecs/<selector>.tfstate`, `eks/<selector>.tfstate`

Validate all stacks with `make terraform-check` before changing workflows.

## Verify and operate

For ECS, test the workflow's Application URL, ECS steady state, ALB target health, CloudWatch log group, dashboard, and alarms. For EKS, run:

```bash
kubectl --namespace agentic-ai get deployments,pods,services
kubectl --namespace agentic-ai rollout status deployment/<dns-safe-selector>
```

Use immutable image tags for rollback, rotate the secret in Secrets Manager, and destroy unused application stacks to stop charges. The workflows do not create the account, VPC, S3 bucket, EKS cluster, DNS, certificates, or organization-level IAM because those are platform-owner decisions.

Follow the complete [observability and incident workflow](../projects/README.md#12-observe-and-operate-the-project) after deployment.

When the exercise is finished, follow [AWS services, Terraform state, and project cleanup](aws_services_and_cleanup.md) and run the guarded undeploy workflow.
