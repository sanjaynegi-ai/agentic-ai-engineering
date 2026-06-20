# EKS application deployment

The executable deployment configuration lives in `infra/terraform/ecr` and `infra/terraform/eks`. Dispatch `.github/workflows/deploy-eks-manual.yml`; Terraform reconciles Kubernetes resources through the provider. See `docs/project_to_aws.md`.
