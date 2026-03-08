from typing import Any

import pandas as pd

from app.utils.constants import (
    CATEGORICAL_FEATURES,
    CLASSIFIER_FEATURES,
    DEFAULT_SCENARIO_VALUES,
    REGRESSION_FEATURES,
)


def get_regression_features() -> list[str]:
    return list(REGRESSION_FEATURES)


def get_classifier_features() -> list[str]:
    return list(CLASSIFIER_FEATURES)


def get_categorical_feature_indices(features: list[str]) -> list[int]:
    return [idx for idx, name in enumerate(features) if name in CATEGORICAL_FEATURES]


def prepare_regression_frame(df: pd.DataFrame) -> pd.DataFrame:
    return _cast_categoricals(df[get_regression_features()].copy())


def prepare_regression_target(df: pd.DataFrame) -> pd.Series:
    return df["observed_count_log_cfu_g"]


def prepare_classifier_frame(df: pd.DataFrame) -> pd.DataFrame:
    deduped = df.sort_values(["study_id", "time_days"]).groupby("study_id", as_index=False).last()
    return _cast_categoricals(deduped[get_classifier_features()].copy())


def prepare_classifier_target(df: pd.DataFrame) -> pd.Series:
    deduped = df.sort_values(["study_id", "time_days"]).groupby("study_id", as_index=False).last()
    return deduped["study_final_exceeds_regulatory_threshold"].astype(int)


def scenario_to_base_features(scenario: dict[str, Any]) -> dict[str, Any]:
    base = DEFAULT_SCENARIO_VALUES.copy()
    base.update(scenario)
    base["max_time_days"] = max(base.get("max_time_days", 42), base.get("target_shelf_life_days", 42))
    return base


def scenario_to_regression_rows(scenario: dict[str, Any], days: list[int]) -> pd.DataFrame:
    base = scenario_to_base_features(scenario)
    rows = []
    for day in days:
        row = {feature: base.get(feature) for feature in get_regression_features()}
        row["time_days"] = day
        rows.append(row)
    return _cast_categoricals(pd.DataFrame(rows, columns=get_regression_features()))


def scenario_to_classifier_row(scenario: dict[str, Any]) -> pd.DataFrame:
    base = scenario_to_base_features(scenario)
    row = {feature: base.get(feature) for feature in get_classifier_features()}
    return _cast_categoricals(pd.DataFrame([row], columns=get_classifier_features()))


def _cast_categoricals(frame: pd.DataFrame) -> pd.DataFrame:
    for column in frame.columns:
        if column in CATEGORICAL_FEATURES:
            frame[column] = frame[column].astype(str)
    return frame
