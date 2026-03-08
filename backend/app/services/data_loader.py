import json
from pathlib import Path

import pandas as pd

from app.core.config import get_settings
from app.utils.constants import REQUIRED_DATASET_COLUMNS
from app.utils.validation import ensure_required_columns


def load_dataset(path: Path | None = None) -> pd.DataFrame:
    settings = get_settings()
    dataset_path = path or settings.data_path
    df = pd.read_csv(dataset_path)
    ensure_required_columns(df.columns, REQUIRED_DATASET_COLUMNS)
    return df


def dataset_metadata(df: pd.DataFrame) -> dict:
    return {
        "dataset_version": get_settings().dataset_version,
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "is_synthetic": bool(df["is_synthetic"].mode().iloc[0]),
        "data_source": str(df["data_source"].mode().iloc[0]),
    }


def save_json_report(payload: dict, filename: str) -> Path:
    settings = get_settings()
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = settings.reports_dir / filename
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path
