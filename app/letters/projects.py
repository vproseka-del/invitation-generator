import json
from pathlib import Path

PROJECTS_PATH = Path(__file__).resolve().parents[2] / "knowledge" / "projects"

REGISTRY_FILE = PROJECTS_PATH / "index.json"


def load_registry():
    with open(REGISTRY_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_project_arguments(project_id):
    registry = load_registry()
    entry = registry["projects"].get(project_id)
    if not entry:
        raise ValueError(f"Неизвестный проект: {project_id}")

    path = PROJECTS_PATH / entry["file"]
    with open(path, encoding="utf-8") as f:
        return json.load(f)
