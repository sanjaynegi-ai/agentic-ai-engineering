import json
from pathlib import Path

from scripts.resolve_project import deployment_name, resolve


ROOT = Path(__file__).resolve().parents[1]


def test_resolves_practice_project():
    result = resolve("customer_support_router_openai_agents_sdk", "sha-123")
    assert result["context"] == "projects/openai_agents_sdk_projects/customer_support_router"
    assert result["evaluator"] == "project"
    assert result["deployment_name"] == "customer-support-router-openai-agents-sdk"


def test_resolves_comparison_project():
    result = resolve("comparison_travel_agent_no_framework", "local")
    assert result["context"] == "projects/comparison_agent/no_framework"
    assert result["evaluator"] == "comparison"


def test_long_deployment_names_are_dns_safe_and_stable():
    name = deployment_name("a_very_long_project_name_" * 5)
    assert len(name) <= 63
    assert "_" not in name


def test_every_catalog_selector_is_available_in_each_aws_workflow():
    catalog = json.loads((ROOT / "projects/project_catalog.json").read_text(encoding="utf-8"))
    selectors = {
        f"{project}_{implementation}"
        for project, implementations in catalog.items()
        for implementation in implementations
    }
    workflow_names = (
        "build-push-ecr.yml",
        "deploy-ecs-manual.yml",
        "deploy-eks-manual.yml",
        "undeploy-aws-project.yml",
    )
    for workflow_name in workflow_names:
        text = (ROOT / ".github/workflows" / workflow_name).read_text(encoding="utf-8")
        missing = sorted(selector for selector in selectors if f"- {selector}" not in text)
        assert not missing, f"{workflow_name} missing selectors: {missing}"


def test_undeploy_workflow_has_destructive_action_guards():
    text = (ROOT / ".github/workflows/undeploy-aws-project.yml").read_text(encoding="utf-8")
    assert "confirm_project" in text
    assert "environment: production" in text
    assert "aws-project-${{ inputs.project }}" in text
    assert text.index("Destroy ECS application stack") < text.index(
        "Destroy EKS application stack"
    ) < text.index("Destroy ECR repository")
    assert 'force_delete=true' in text
