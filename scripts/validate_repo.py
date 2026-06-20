from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = {"travel_planner_agent", "customer_support_router", "research_assistant_agent"}
CATALOG_PROJECTS = {*PROJECTS, "comparison_travel_agent"}


def validate_notebooks() -> list[str]:
    errors: list[str] = []
    notebooks = list((ROOT / "notebooks").rglob("*.ipynb"))
    if len(notebooks) != 18:
        errors.append(f"Expected 18 notebooks, found {len(notebooks)}")
    for path in notebooks:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Invalid notebook {path.relative_to(ROOT)}: {exc}")
            continue
        if len(data.get("cells", [])) < 8:
            errors.append(f"Notebook has fewer than 8 cells: {path.relative_to(ROOT)}")
    return errors


def validate_project_pairs() -> list[str]:
    errors: list[str] = []
    roots = {
        "no_framework": ROOT / "projects/no_framework_projects",
        "openai_agents_sdk": ROOT / "projects/openai_agents_sdk_projects",
    }
    for implementation, root in roots.items():
        found = {path.name for path in root.iterdir() if path.is_dir()}
        if found != PROJECTS:
            errors.append(
                f"{implementation} projects: expected {sorted(PROJECTS)}, found {sorted(found)}"
            )

    catalog = json.loads((ROOT / "projects/project_catalog.json").read_text(encoding="utf-8"))
    if set(catalog) != CATALOG_PROJECTS:
        errors.append(
            f"Catalog projects: expected {sorted(CATALOG_PROJECTS)}, found {sorted(catalog)}"
        )
    for project in CATALOG_PROJECTS:
        for implementation in ("no_framework", "openai_agents_sdk"):
            context = catalog.get(project, {}).get(implementation, {}).get("context")
            if not context or not (ROOT / context).is_dir():
                errors.append(f"Missing catalog path for {implementation}/{project}")
    return errors


def main() -> int:
    errors = [*validate_notebooks(), *validate_project_pairs()]
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: notebooks are valid and all projects form complete no-framework/SDK pairs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
