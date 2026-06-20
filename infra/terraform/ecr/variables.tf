variable "aws_region" { type = string }
variable "project_name" { type = string }
variable "force_delete" {
  description = "Allow repository deletion when it still contains images. Enable only during deliberate teardown."
  type        = bool
  default     = false
}
