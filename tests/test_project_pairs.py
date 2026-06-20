import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ("travel_planner_agent", "customer_support_router", "research_assistant_agent")
IMPLEMENTATIONS = ("no_framework_projects", "openai_agents_sdk_projects")
REQUIRED_FILES = (
    "README.md",
    "app.py",
    "pyproject.toml",
    "Dockerfile",
    "docker-compose.yml",
    ".dockerignore",
    ".env.example",
    "uv.lock",
    "prompts/system.md",
    "tests/test_service.py",
)


def load_service(project: str, implementation: str):
    path = ROOT / "projects" / implementation / project / "src" / project / "service.py"
    module_name = f"pair_test_{implementation}_{project}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_project_folders_are_one_to_one_pairs():
    no_framework = {
        path.name for path in (ROOT / "projects/no_framework_projects").iterdir() if path.is_dir()
    }
    sdk = {
        path.name
        for path in (ROOT / "projects/openai_agents_sdk_projects").iterdir()
        if path.is_dir()
    }
    assert no_framework == sdk == set(PROJECTS)


def test_each_implementation_has_runnable_project_files():
    for implementation in IMPLEMENTATIONS:
        for project in PROJECTS:
            project_root = ROOT / "projects" / implementation / project
            missing = [name for name in REQUIRED_FILES if not (project_root / name).is_file()]
            assert not missing, f"{implementation}/{project} missing {missing}"


def test_each_pair_exposes_the_same_output_fields():
    for project in PROJECTS:
        manual = load_service(project, "no_framework_projects")
        sdk = load_service(project, "openai_agents_sdk_projects")
        manual_fields = set(manual.run(sample_input(project)).__class__.model_fields)
        sdk_fields = set(sdk.run(sample_input(project)).__class__.model_fields)
        assert manual_fields == sdk_fields


def test_catalog_contains_both_sides_of_every_pair():
    catalog = json.loads((ROOT / "projects/project_catalog.json").read_text(encoding="utf-8"))
    assert set(catalog) == {*PROJECTS, "comparison_travel_agent"}
    for project, implementations in catalog.items():
        assert set(implementations) == {"no_framework", "openai_agents_sdk"}
        for config in implementations.values():
            assert (ROOT / config["context"]).is_dir(), project


def test_comparison_projects_have_container_inputs():
    for implementation in ("no_framework", "openai_agents_sdk"):
        root = ROOT / "projects/comparison_agent" / implementation
        for name in ("Dockerfile", ".dockerignore", ".env.example", "uv.lock"):
            assert (root / name).is_file(), f"comparison/{implementation} missing {name}"


def sample_input(project: str) -> str:
    return {
        "travel_planner_agent": "Plan a 2-day Jaipur trip for 4 people",
        "customer_support_router": "I was charged twice",
        "research_assistant_agent": "What do guardrails constrain?",
    }[project]
