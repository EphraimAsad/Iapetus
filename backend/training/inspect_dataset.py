import json

from app.services.data_loader import dataset_metadata, load_dataset, save_json_report
from app.utils.constants import LEAKAGE_COLUMNS


def main() -> None:
    df = load_dataset()
    report = {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "columns": list(df.columns),
        "dtypes": {column: str(dtype) for column, dtype in df.dtypes.items()},
        "missingness": df.isna().sum().astype(int).to_dict(),
        "numeric_summary": df.describe(include=["number"]).round(4).to_dict(),
        "categorical_uniques": {},
        "targets": [
            "observed_count_log_cfu_g",
            "study_final_exceeds_regulatory_threshold",
            "study_final_log_cfu_g",
        ],
        "likely_leakage_columns": LEAKAGE_COLUMNS,
        "dataset_metadata": dataset_metadata(df),
    }

    for column in df.select_dtypes(include=["object", "bool"]).columns:
        values = df[column].dropna().unique().tolist()
        report["categorical_uniques"][column] = {
            "count": int(df[column].nunique(dropna=True)),
            "sample_values": values[:20],
        }

    report_path = save_json_report(report, "dataset_inspection_report.json")
    print("DATASET INSPECTION")
    print(json.dumps(report["shape"], indent=2))
    print(f"Saved report to: {report_path}")
    print("Targets:", ", ".join(report["targets"]))
    print("Likely leakage columns:", ", ".join(report["likely_leakage_columns"]))


if __name__ == "__main__":
    main()
