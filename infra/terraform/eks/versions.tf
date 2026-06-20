terraform {
  required_version = ">= 1.10.0"
  backend "s3" {}
  required_providers {
    aws        = { source = "hashicorp/aws", version = "~> 6.0" }
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.38" }
  }
}
provider "aws" { region = var.aws_region }
data "aws_eks_cluster" "course" { name = var.eks_cluster_name }
data "aws_eks_cluster_auth" "course" { name = var.eks_cluster_name }
provider "kubernetes" {
  host                   = data.aws_eks_cluster.course.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.course.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.course.token
}
