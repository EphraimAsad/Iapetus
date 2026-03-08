from datetime import datetime, timezone

from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

from app.core.config import get_settings
from app.services.data_loader import dataset_metadata, load_dataset
from app.services.feature_builder import (
    get_categorical_feature_indices,
    get_classifier_features,
    prepare_classifier_frame,
    prepare_classifier_target,
)
from app.services.model_registry import save_model_bundle

try:
    from catboost import CatBoostClassifier
except ModuleNotFoundError as exc:
    raise SystemExit("catboost is required to train the classifier. Install backend dependencies first.") from exc


def main() -> None:
    df = load_dataset()
    X = prepare_classifier_frame(df)
    y = prepare_classifier_target(df)
    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = CatBoostClassifier(
        iterations=300,
        depth=6,
        learning_rate=0.05,
        loss_function="Logloss",
        eval_metric="AUC",
        verbose=False,
        random_seed=42,
    )
    cat_indices = get_categorical_feature_indices(get_classifier_features())
    model.fit(X_train, y_train, cat_features=cat_indices, eval_set=(X_valid, y_valid), use_best_model=True)

    probabilities = model.predict_proba(X_valid)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    metrics = {
        "roc_auc": round(float(roc_auc_score(y_valid, probabilities)), 4),
        "pr_auc": round(float(average_precision_score(y_valid, probabilities)), 4),
        "f1": round(float(f1_score(y_valid, predictions)), 4),
        "confusion_matrix": confusion_matrix(y_valid, predictions).tolist(),
    }
    metadata = {
        "model_type": "CatBoostClassifier",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "features": get_classifier_features(),
        "categorical_feature_indices": cat_indices,
        "metrics": metrics,
        "dataset_metadata": dataset_metadata(df),
        "threshold_cfu_g": get_settings().threshold_cfu_g,
    }
    save_model_bundle(model, metadata, "classifier")
    print("Saved classifier artifact with metrics:", metrics)


if __name__ == "__main__":
    main()
