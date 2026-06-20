from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ("travel_planner_agent", "customer_support_router", "research_assistant_agent")
IMPLEMENTATIONS = {
    "no_framework": "no_framework_projects",
    "openai_agents_sdk": "openai_agents_sdk_projects",
}


def load_service(project: str, implementation: str):
    service_path = (
        ROOT
        / "projects"
        / IMPLEMENTATIONS[implementation]
        / project
        / "src"
        / project
        / "service.py"
    )
    module_name = f"project_eval_{implementation}_{project}"
    spec = importlib.util.spec_from_file_location(module_name, service_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {service_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", choices=["all", *PROJECTS], default="all")
    parser.add_argument(
        "--implementation", choices=["all", *IMPLEMENTATIONS], default="all"
    )
    args = parser.parse_args()
    failures: list[str] = []
    cases = [
        json.loads(line)
        for line in (ROOT / "evals/data/project_cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    selected_implementations = (
        IMPLEMENTATIONS if args.implementation == "all" else (args.implementation,)
    )

    for case in cases:
        project = case["project"]
        if args.project not in ("all", project):
            continue
        for implementation in selected_implementations:
            module = load_service(project, implementation)
            data = module.run(case["input"]).model_dump(mode="json")
            passed = data.get(case["field"]) == case["expected"]
            label = f"{implementation}/{project}"
            print(f"{'PASS' if passed else 'FAIL'} {label}: {case['input']}")
            if not passed:
                failures.append(label)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
