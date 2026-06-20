from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from .models import AgentRun, EvalCase


ModelT = TypeVar("ModelT", bound=BaseModel)


def _load_jsonl(path: Path, model: type[ModelT]) -> list[ModelT]:
    records: list[ModelT] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(model.model_validate_json(line))
        except Exception as exc:
            raise ValueError(f"Invalid record at {path}:{line_number}: {exc}") from exc
    return records


def load_cases(path: Path) -> list[EvalCase]:
    return _load_jsonl(path, EvalCase)


def load_runs(path: Path) -> list[AgentRun]:
    return _load_jsonl(path, AgentRun)


def write_report(path: Path, report: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
