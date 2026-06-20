# Terraform deployment stacks

These stacks are application-level building blocks orchestrated by GitHub Actions.

| Stack | Owns | Does not own |
|---|---|---|
| `ecr/` | Private ECR repository, immutable tags, scan-on-push, encryption, lifecycle policy | Docker image build |
| `ecs/` | Per-selector Fargate cluster/service, task definition, IAM roles, CloudWatch logs, Container Insights, alarms, dashboard, ALB, target group, security groups | VPC, subnets, DNS, TLS certificate, Secrets Manager secret, SNS notification routing |
| `eks/` | Deployment and LoadBalancer Service in namespace `agentic-ai` | EKS cluster/nodes, namespace, Kubernetes Secret, cluster IAM/access entry |

GitHub Actions configures an S3 backend per selector with encryption and native state locking. The state bucket must already be private, encrypted, versioned, and restricted to the deployment role.

The manual undeploy workflow uses the same backend keys, destroys ECS and EKS application states before ECR, enables ECR `force_delete` only for deliberate teardown, and retains empty state/history in S3. It never destroys shared bootstrap infrastructure.

ECS receives only a Secrets Manager ARN; the task execution role reads the secret at startup. EKS references an existing Kubernetes Secret. The workflow creates that Secret from AWS Secrets Manager before Terraform runs, preventing the OpenAI API key from being persisted in Terraform state.

Validate without applying:

```bash
terraform fmt -check -recursive infra/terraform
terraform -chdir=infra/terraform/ecr init -backend=false
terraform -chdir=infra/terraform/ecr validate
terraform -chdir=infra/terraform/ecs init -backend=false
terraform -chdir=infra/terraform/ecs validate
terraform -chdir=infra/terraform/eks init -backend=false
terraform -chdir=infra/terraform/eks validate
```

See [`projects/README.md`](../../projects/README.md) for the full local-to-AWS process and credential model.
See [`docs/aws_services_and_cleanup.md`](../../docs/aws_services_and_cleanup.md) for service ownership and the complete teardown runbook.
