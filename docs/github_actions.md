# GitHub Actions

CI syncs the frozen `uv.lock`, runs tests/evals, and checks lint. AWS workflows are manual and use a protected `production` environment.

Authentication uses GitHub OIDC and `aws-actions/configure-aws-credentials`; do not configure long-lived `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` secrets. Store the OpenAI key in AWS Secrets Manager and expose only its ARN through `OPENAI_SECRET_ARN`.

The manual workflows resolve project selectors from `projects/project_catalog.json`, validate the chosen implementation, create ECR with Terraform, push an immutable commit-SHA image, and optionally apply the ECS or EKS application stack. Concurrency groups prevent two runs from changing the same selector simultaneously.

`undeploy-aws-project.yml` uses the same selector concurrency group and remote state. It requires the selector to be retyped, detects non-empty state, destroys ECS and EKS application resources before ECR, and preserves shared infrastructure and state history. Keep the `production` environment protected with required reviewers.

Required GitHub environment variables and workflow details are documented in [`projects/README.md`](../projects/README.md). Service ownership and teardown recovery are documented in [`aws_services_and_cleanup.md`](aws_services_and_cleanup.md).
