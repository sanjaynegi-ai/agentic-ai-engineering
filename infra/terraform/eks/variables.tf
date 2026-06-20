variable "aws_region" { type = string }
variable "eks_cluster_name" { type = string }
variable "project_name" { type = string }
variable "image_uri" { type = string }
variable "kubernetes_namespace" {
  type    = string
  default = "agentic-ai"
}
variable "openai_secret_name" {
  type    = string
  default = "openai-api"
}
