import math
from datetime import datetime, timezone

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from app.core.config import get_settings
from app.services.data_loader import dataset_metadata, load_dataset
from app.services.feature_builder import (
    get_categorical_feature_indices,
    get_regression_features,
    prepare_regression_frame,
    prepare_regression_target,
)
from app.services.model_registry import save_model_bundle

try:
    from catboost import CatBoostRegressor
except ModuleNotFoundError as exc:
    raise SystemExit("catboost is required to train the regressor. Install backend dependencies first.") from exc


def main() -> None:
    df = load_dataset()
    X = prepare_regression_frame(df)
    y = prepare_regression_target(df)
    stratify = (df["dataset_split"] == "test").astype(int)
    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=stratify
    )

    model = CatBoostRegressor(
        iterations=300,
        depth=6,
        learning_rate=0.05,
        loss_function="RMSE",
        eval_metric="RMSE",
        verbose=False,
        random_seed=42,
    )
    cat_indices = get_categorical_feature_indices(get_regression_features())
    model.fit(X_train, y_train, cat_features=cat_indices, eval_set=(X_valid, y_valid), use_best_model=True)

    predictions = model.predict(X_valid)
    metrics = {
        "rmse": round(float(math.sqrt(mean_squared_error(y_valid, predictions))), 4),
        "mae": round(float(mean_absolute_error(y_valid, predictions)), 4),
        "r2": round(float(r2_score(y_valid, predictions)), 4),
    }
    metadata = {
        "model_type": "CatBoostRegressor",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "features": get_regression_features(),
        "categorical_feature_indices": cat_indices,
        "metrics": metrics,
        "dataset_metadata": dataset_metadata(df),
        "threshold_cfu_g": get_settings().threshold_cfu_g,
    }
    save_model_bundle(model, metadata, "regressor")
    print("Saved regressor artifact with metrics:", metrics)


if __name__ == "__main__":
    main()
