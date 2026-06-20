# AWS services, Terraform state, and project cleanup

This guide explains every AWS service used by the project lifecycle, which layer owns it, what it costs, and what the manual undeploy workflow removes.

## Architecture at a glance

```text
GitHub Actions
  |-- GitHub OIDC -> AWS STS -> short-lived deployment credentials
  |-- Terraform remote state -> private S3 bucket + native lockfile
  |-- Docker image -> private ECR repository
  |-- ECS path -> Fargate service -> ALB -> application
  `-- EKS path -> existing EKS cluster -> Kubernetes Service -> application

OpenAI API key -> AWS Secrets Manager
Runtime logs/metrics -> CloudWatch Logs, metrics, alarms, dashboard
```

## AWS service inventory

| Service | Purpose | Created by this repository? | Removed by project undeploy? | Main cost consideration |
|---|---|---:|---:|---|
| IAM | Deployment and runtime permissions | ECS task/execution roles are created; GitHub deployment role is external | Project ECS roles: yes. Shared GitHub role: no | No direct charge; permissions are security-critical |
| GitHub OIDC / AWS STS | Exchanges a GitHub identity token for short-lived AWS credentials | No; account bootstrap | No | No direct charge |
| Amazon S3 | Stores encrypted Terraform state and lock objects | No; bootstrap prerequisite | No; state history is retained | Small storage/request cost |
| Amazon ECR | Stores private immutable Docker images | Yes, one repository per selector | Yes, including contained images | Image storage and data transfer |
| AWS Secrets Manager | Stores the OpenAI API key | No; bootstrap prerequisite | No; shared secret is retained | Per-secret and API-call charges |
| Amazon ECS | Schedules the container task | Yes on ECS path | Yes | Control plane has no separate charge; tasks do |
| AWS Fargate | Supplies serverless container compute | Yes through ECS service | Yes | vCPU and memory while tasks run |
| Elastic Load Balancing | Exposes the ECS application | ALB, listener, target group | Yes | ALB hours and capacity units |
| Amazon VPC | Networking boundary | No; existing VPC/subnets are supplied | No | NAT gateways/public IPv4 can dominate cost |
| Security Groups | Restrict ALB and application traffic | Yes on ECS path | Yes | No direct charge |
| CloudWatch Logs | Stores ECS application logs | Yes | Yes | Ingestion, retention, and query volume |
| CloudWatch Metrics/Alarms/Dashboard | ECS health, latency, CPU, memory, errors | Yes | Yes | Custom/dashboard/alarm usage; standard metrics vary |
| Amazon EKS | Kubernetes control plane | No; existing cluster is supplied | No | Cluster hourly charge plus worker capacity |
| Kubernetes Deployment/Service | Runs and exposes the project on EKS | Yes through Terraform | Yes | Worker compute and cloud load balancer |
| Kubernetes namespace/Secret | Shared runtime namespace and API key | Created/refreshed by workflow, outside project Terraform state | No; shared for other projects | No direct Kubernetes charge |

The undeploy workflow removes resources managed by the selected project's Terraform states. It deliberately does not infer ownership of shared infrastructure.

## Terraform state location

The GitHub environment variable `TF_STATE_BUCKET` points to an existing private S3 bucket. Each selector uses independent state objects:

```text
s3://<TF_STATE_BUCKET>/ecr/<selector>.tfstate
s3://<TF_STATE_BUCKET>/ecs/<selector>.tfstate
s3://<TF_STATE_BUCKET>/eks/<selector>.tfstate
```

Terraform is initialized with:

```text
encrypt=true
use_lockfile=true
```

The lock object prevents concurrent Terraform operations against the same state. All build, deploy, and undeploy workflows use the same selector-level concurrency group as an additional GitHub-side guard.

## State bucket best practices

- Use a dedicated bucket per AWS account/environment or a rigorously separated prefix strategy.
- Enable S3 Block Public Access, default encryption (prefer a customer-managed KMS key when required), and versioning.
- Restrict object access to the GitHub OIDC deployment role and a small administrator/break-glass group.
- Permit the deployment role only the required bucket listing, state object, and lock object actions/prefixes.
- Record S3 and role activity in CloudTrail.
- Retain state versions long enough to recover from accidental state corruption or deletion.
- Do not place application secrets directly in Terraform variables/resources when that would persist them in state.
- Never manually delete or edit the current state object as a normal cleanup method.
- Never delete the state bucket before every managed stack has been deliberately destroyed or migrated.

After `terraform destroy`, the state object normally remains with an empty `resources` array. This is desirable audit/recovery history. The undeploy workflow checks whether state contains managed resources, not merely whether the S3 object exists.

## Undeploy workflow safety controls

Workflow: `.github/workflows/undeploy-aws-project.yml`

The workflow is manual and protected by the GitHub `production` environment. It requires:

1. Selecting the exact scenario/framework selector.
2. Retyping that selector into `confirm_project`.
3. Passing any configured production-environment reviewer approval.
4. Acquiring the selector's shared GitHub concurrency group so deploy and undeploy cannot overlap.
5. Authenticating through GitHub OIDC; no stored AWS access keys are used.

The workflow downloads each state object and uses Python's JSON parser to check whether it contains managed resources. Empty or missing stacks are skipped.

## Destruction order

The workflow always uses this dependency-safe order:

1. **ECS state**, when non-empty:
   - ECS service and tasks
   - Task definition ownership in state
   - ALB, listener, and target group
   - Security groups
   - CloudWatch alarms, dashboard, and log group
   - Project ECS cluster
   - Project execution/task IAM roles and inline policies
2. **EKS application state**, when non-empty:
   - Kubernetes Deployment and pods
   - Kubernetes LoadBalancer Service and its cloud load balancer
3. **ECR state**, when non-empty:
   - Lifecycle policy
   - ECR repository and all project images (`force_delete=true` only during teardown)

ECR is last. If ECS or EKS destruction fails, the workflow stops and preserves the image needed for recovery or rollback.

Each stack runs `terraform plan -destroy` first, saves the plan, applies that exact plan, and verifies that `terraform state list` is empty.

## Resources intentionally preserved

The workflow does not destroy:

- Terraform S3 state bucket, state history, or KMS key
- GitHub OIDC provider or shared deployment role
- Existing VPC, subnets, route tables, NAT gateways, or account networking
- Existing EKS cluster, node groups, add-ons, or cluster access entries
- Shared `agentic-ai` Kubernetes namespace and `openai-api` Secret
- AWS Secrets Manager OpenAI secret
- DNS zones, certificates, organization controls, budgets, or audit infrastructure

These resources are shared or were not created by the project states. Destroying them from a project workflow could break unrelated applications.

## Required GitHub environment configuration

The undeploy workflow reuses the deployment variables:

| Variable | Why destruction needs it |
|---|---|
| `AWS_DEPLOY_ROLE_ARN` | OIDC role assumed by GitHub |
| `AWS_REGION` | Provider and state backend region |
| `TF_STATE_BUCKET` | Finds the authoritative stack state |
| `OPENAI_SECRET_ARN` | Required ECS variable while constructing the destroy plan |
| `AWS_VPC_ID` | Required ECS variable while constructing the destroy plan |
| `AWS_PUBLIC_SUBNET_IDS_JSON` | Required ECS variable while constructing the destroy plan |
| `EKS_CLUSTER` | Configures the Kubernetes provider when EKS state is non-empty |

The deployment role needs permissions to read/write the state and lock objects and to delete resources managed by the ECR/ECS/EKS stacks. For EKS cleanup it also needs cluster access and Kubernetes authorization to delete the Deployment and Service.

## Running a full project cleanup

1. Open **GitHub → Actions → Terraform undeploy project from AWS**.
2. Choose the deployed selector, for example `customer_support_router_openai_agents_sdk`.
3. Paste that exact selector into `confirm_project`.
4. Select **Run workflow** and approve the protected environment deployment if prompted.
5. Review the job summary to see which state stacks were found and destroyed.

Do not cancel the workflow during an active Terraform apply. If cancellation is unavoidable, rerun the same undeploy workflow; remote state and locking allow Terraform to reconcile the remaining resources.

## Verify that billable project resources are gone

Use the selector and workflow summary to verify:

```bash
aws ecr describe-repositories --repository-names agentic-ai/<selector>
aws ecs list-clusters
aws elbv2 describe-load-balancers
aws logs describe-log-groups --log-group-name-prefix /ecs/agentic-ai/
aws cloudwatch describe-alarms --alarm-name-prefix <dns-safe-selector>
kubectl --namespace agentic-ai get deployment,service
```

Expected results are repository-not-found for ECR and no matching ECS/EKS/ALB/log/alarm resources for the selector. Shared prerequisites should still exist.

Also review AWS Cost Explorer after billing data catches up. Resource deletion stops future use charges but does not erase already incurred charges, and delayed metering can remain visible for a while.

## Failure recovery

### Terraform reports a state lock

First verify that no deploy/undeploy run is active. Do not force-unlock an active operation. If a failed run left an orphaned lock, use `terraform force-unlock` only after confirming the lock ID and state key.

### ECS destroy fails

Inspect service events, target deregistration, IAM denial messages, and dependency errors. Fix access/configuration and rerun. ECR is preserved because it is destroyed last.

### EKS destroy cannot reach the cluster

Confirm the external cluster still exists, the workflow role has an EKS access entry, and the Kubernetes provider can authenticate. If the cluster was deleted outside Terraform, state recovery requires deliberate `terraform state rm` operations by an administrator after confirming the Kubernetes resources truly no longer exist.

### ECR repository is not empty

The undeploy workflow passes `force_delete=true` only to the ECR destroy plan. A normal deploy keeps `force_delete=false`, protecting images from accidental repository deletion.

### State and AWS disagree

Do not blindly delete state. Use `terraform plan`, AWS inventory commands, and—when appropriate—`terraform import` or narrowly targeted `terraform state rm`. Preserve an S3 state version before any manual repair.

## Cost-control routine for students

- Deploy only the selector currently being studied.
- Prefer ECS over maintaining a dedicated EKS cluster unless Kubernetes is the lesson.
- Use immutable images and avoid duplicate repositories.
- Follow logs and metrics while testing, then undeploy immediately after the exercise.
- Confirm ALBs, Fargate tasks, ECR images, and project log groups are gone.
- Keep account-level AWS Budgets and billing alerts outside the project stack so cleanup cannot delete them.
