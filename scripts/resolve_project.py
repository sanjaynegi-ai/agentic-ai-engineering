from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "projects/project_catalog.json"
TAG_PATTERN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$")


def deployment_name(selection: str) -> str:
    normalized = selection.replace("_", "-").lower()
    if len(normalized) <= 63:
        return normalized
    digest = hashlib.sha256(normalized.encode()).hexdigest()[:8]
    return f"{normalized[:54].rstrip('-')}-{digest}"


def resolve(selection: str, image_tag: str | None = None) -> dict[str, str | int]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    matches = [
        (project, implementation, config)
        for project, implementations in catalog.items()
        for implementation, config in implementations.items()
        if selection == f"{project}_{implementation}"
    ]
    if len(matches) != 1:
        valid = sorted(
            f"{project}_{implementation}"
            for project, implementations in catalog.items()
            for implementation in implementations
        )
        raise ValueError(f"Unknown project selection {selection!r}. Choose one of: {valid}")

    project, implementation, config = matches[0]
    context = ROOT / config["context"]
    if not context.is_dir():
        raise ValueError(f"Project context does not exist: {config['context']}")
    tag = image_tag or os.getenv("GITHUB_SHA", "local")
    if not TAG_PATTERN.fullmatch(tag):
        raise ValueError(f"Invalid Docker image tag: {tag!r}")
    return {
        "selection": selection,
        "project": project,
        "implementation": implementation,
        "context": config["context"],
        "port": config["port"],
        "evaluator": config["evaluator"],
        "deployment_name": deployment_name(selection),
        "image_tag": tag,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve a project deployment selector")
    parser.add_argument("--selection", required=True)
    parser.add_argument("--image-tag")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    result = resolve(args.selection, args.image_tag)
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as output:
            for key, value in result.items():
                output.write(f"{key}={value}\n")
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
