import json
from typing import Any

import joblib

from app.core.config import get_settings


def artifact_path(name: str):
    settings = get_settings()
    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
    return settings.artifacts_dir / name


def save_model_bundle(model: Any, metadata: dict[str, Any], model_name: str) -> None:
    joblib.dump(model, artifact_path(f"{model_name}.joblib"))
    artifact_path(f"{model_name}_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def load_model_bundle(model_name: str):
    model = joblib.load(artifact_path(f"{model_name}.joblib"))
    metadata = json.loads(artifact_path(f"{model_name}_metadata.json").read_text(encoding="utf-8"))
    return model, metadata
