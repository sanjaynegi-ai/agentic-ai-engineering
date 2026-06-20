# AWS EKS with Terraform

EKS is the Kubernetes path when Kubernetes APIs, policy, or an existing platform justify its cost. The course assumes an existing EKS cluster. The workflow creates the shared namespace and refreshes a Kubernetes Secret from AWS Secrets Manager outside Terraform; `infra/terraform/eks` then reconciles the project Deployment, resource limits, probes, replicas, and LoadBalancer Service. This keeps the API key out of Terraform state. Follow [the end-to-end guide](project_to_aws.md).
