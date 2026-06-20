variable "aws_region" { type = string }
variable "project_name" { type = string }
variable "image_uri" { type = string }
variable "vpc_id" { type = string }
variable "public_subnet_ids" { type = list(string) }
variable "openai_secret_arn" {
  type      = string
  sensitive = true
}
