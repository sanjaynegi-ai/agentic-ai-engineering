setup:
	uv sync --group dev
test:
	uv run pytest
lint:
	uv run ruff check .
notebooks:
	uv run jupyter lab
validate:
	uv run python scripts/validate_repo.py
evals:
	uv run python -m evals.run_evals
evals-live:
	uv run python -m evals.run_evals --mode live
project-evals:
	uv run python -m evals.run_project_evals
terraform-check:
	terraform fmt -check -recursive infra/terraform
	terraform -chdir=infra/terraform/ecr init -backend=false
	terraform -chdir=infra/terraform/ecr validate
	terraform -chdir=infra/terraform/ecs init -backend=false
	terraform -chdir=infra/terraform/ecs validate
	terraform -chdir=infra/terraform/eks init -backend=false
	terraform -chdir=infra/terraform/eks validate

project-check:
	uv run pytest
	uv run ruff check .
	uv run python scripts/validate_repo.py
	uv run python -m evals.run_project_evals
	uv run python -m evals.run_evals
