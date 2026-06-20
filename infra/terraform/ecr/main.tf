resource "aws_ecr_repository" "app" {
  name                 = "agentic-ai/${var.project_name}"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = var.force_delete
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
}
resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name
  policy     = jsonencode({ rules = [{ rulePriority = 1, description = "Keep 30 images", selection = { tagStatus = "any", countType = "imageCountMoreThan", countNumber = 30 }, action = { type = "expire" } }] })
}
