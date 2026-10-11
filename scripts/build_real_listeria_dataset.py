from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "real_listeria" / "raw" / "source_records.csv"
DEFAULT_OUTDIR = ROOT / "data" / "real_listeria" / "processed"
DEFAULT_REPORT = ROOT / "data" / "real_listeria" / "metadata" / "dataset_qc.json"

ALIASES = {
    "source_key": ["source_key", "source", "dataset_source"],
    "source_record_id": ["source_record_id", "record_id", "combase_record_id", "record"],
    "source_doi": ["source_doi", "doi"],
    "organism": ["organism", "pathogen", "species"],
    "product_name_original": ["product_name_original", "food_name", "food", "product_name", "medium"],
    "product_category_original": ["product_category_original", "food_category", "product_category", "category"],
    "temperature_c": ["temperature_c", "temperature", "temp_c", "storage_temperature_c"],
    "ph": ["ph", "pH"],
    "aw": ["aw", "a_w", "water_activity"],
    "time_hours": ["time_hours", "time_h", "time", "hours"],
    "observed_log_cfu_g": ["observed_log_cfu_g", "log_cfu_g", "count_log_cfu_g", "logcount"],
    "observed_value_original": ["observed_value_original", "observed_count", "count", "value"],
    "observed_unit_original": ["observed_unit_original", "unit", "count_unit"],
    "qualifier": ["qualifier", "operator", "count_operator"],
    "provenance_url": ["provenance_url", "source_url", "url"],
}


def first_existing(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    lower = {str(c).lower(): c for c in df.columns}
    for c in candidates:
        if c in df.columns:
            return c
        if c.lower() in lower:
            return lower[c.lower()]
    return None


def canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for canonical, aliases in ALIASES.items():
        col = first_existing(df, aliases)
        out[canonical] = df[col] if col is not None else np.nan
    return out


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().split())


def normalize_product_name(value: object) -> str:
    text = normalize_text(value).lower()
    replacements = {
        "tryptic soy broth": "tsb",
        "tryptic soy broth (tsb)": "tsb",
        "brain heart infusion": "bhi",
        "brain heart infusion broth": "bhi",
    }
    return replacements.get(text, text.replace("/", " ").replace("-", " "))


def normalize_category(value: object, product_name: str) -> str:
    text = normalize_text(value).lower()
    if text:
        return text.replace("/", " ").replace("-", " ")
    p = product_name.lower()
    if any(k in p for k in ["salmon", "tuna", "fish", "seafood"]):
        return "seafood"
    if any(k in p for k in ["beef", "pork", "ham", "sausage", "meat"]):
        return "meat"
    if any(k in p for k in ["chicken", "turkey", "poultry"]):
        return "poultry"
    if any(k in p for k in ["milk", "cheese", "cream", "dairy"]):
        return "dairy"
    if any(k in p for k in ["lettuce", "cabbage", "salad", "vegetable"]):
        return "produce"
    if p in {"tsb", "bhi"} or "broth" in p or "agar" in p:
        return "laboratory_medium"
    return "unknown"


def stable_curve_id(source_key: str, source_record_id: str) -> str:
    base = f"{source_key}|{source_record_id}".encode("utf-8")
    return "curve_" + hashlib.sha1(base).hexdigest()[:16]


def environment_group_id(row: pd.Series) -> str:
    parts = [
        row.get("product_name", ""),
        row.get("product_category", ""),
        f"{row.get('temperature_c', np.nan):.6g}" if pd.notna(row.get("temperature_c")) else "NA",
        f"{row.get('ph', np.nan):.6g}" if pd.notna(row.get("ph")) else "NA",
        f"{row.get('aw', np.nan):.6g}" if pd.notna(row.get("aw")) else "NA",
        f"{row.get('initial_inoculum_log_cfu_g', np.nan):.6g}" if pd.notna(row.get("initial_inoculum_log_cfu_g")) else "NA",
    ]
    return "env_" + hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:16]


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def build(source: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    df = canonicalize_columns(source)
    df["source_key"] = df["source_key"].map(normalize_text)
    df["source_record_id"] = df["source_record_id"].map(normalize_text)
    df["source_doi"] = df["source_doi"].map(normalize_text)
    df["organism"] = df["organism"].map(normalize_text)
    df["product_name_original"] = df["product_name_original"].map(normalize_text)
    df["product_category_original"] = df["product_category_original"].map(normalize_text)
    df["provenance_url"] = df["provenance_url"].map(normalize_text)

    for col in ["temperature_c", "ph", "aw", "time_hours", "observed_log_cfu_g", "observed_value_original"]:
        df[col] = numeric(df[col])

    df["product_name"] = df["product_name_original"].map(normalize_product_name)
    df["product_category"] = [normalize_category(c, p) for c, p in zip(df["product_category_original"], df["product_name"])]

    # Restrict to L. monocytogenes-like labels only.
    is_lm = df["organism"].str.lower().str.contains("listeria monocytogenes", na=False)
    df = df.loc[is_lm].copy()

    # A source row cannot enter the canonical set without a source and record identifier.
    missing_id = (df["source_key"] == "") | (df["source_record_id"] == "")
    excluded_missing_ids = int(missing_id.sum())
    df = df.loc[~missing_id].copy()

    df["curve_id"] = [stable_curve_id(a, b) for a, b in zip(df["source_key"], df["source_record_id"])]

    # Remove exact duplicate observations while preserving replicate curves with distinct record IDs.
    dedupe_cols = ["curve_id", "time_hours", "observed_log_cfu_g"]
    before_dedupe = len(df)
    df = df.drop_duplicates(dedupe_cols, keep="first").copy()
    exact_duplicates_removed = before_dedupe - len(df)

    curve_rows = []
    obs_rows = []
    exclusions = []

    for curve_id, g in df.groupby("curve_id", sort=True):
        g = g.sort_values("time_hours").copy()
        first = g.iloc[0]
        time0 = g.loc[np.isclose(g["time_hours"].fillna(np.inf), 0.0)]
        initial = float(time0["observed_log_cfu_g"].iloc[0]) if not time0.empty and pd.notna(time0["observed_log_cfu_g"].iloc[0]) else np.nan
        n_valid = int(g[["time_hours", "observed_log_cfu_g"]].dropna().shape[0])
        has_zero = bool(not time0.empty and pd.notna(initial))
        complete_inputs = all(pd.notna(first[k]) for k in ["temperature_c", "ph", "aw"]) and has_zero and bool(first["product_name"])
        benchmark_eligible = (
            complete_inputs
            and n_valid >= 5
            and 0 <= float(first["temperature_c"]) <= 25
        )

        curve = {
            "curve_id": curve_id,
            "source_key": first["source_key"],
            "source_record_id": first["source_record_id"],
            "source_doi": first["source_doi"],
            "organism": first["organism"],
            "product_name_original": first["product_name_original"],
            "product_name": first["product_name"],
            "product_category_original": first["product_category_original"],
            "product_category": first["product_category"],
            "temperature_c": first["temperature_c"],
            "ph": first["ph"],
            "aw": first["aw"],
            "initial_inoculum_log_cfu_g": initial,
            "n_timepoints": n_valid,
            "has_time_zero": has_zero,
            "core_complete": bool(benchmark_eligible),
            "provenance_url": first["provenance_url"],
        }
        curve["environment_group_id"] = environment_group_id(pd.Series(curve))
        curve_rows.append(curve)

        reasons = []
        if not has_zero:
            reasons.append("missing_time_zero")
        if n_valid < 5:
            reasons.append("fewer_than_5_timepoints")
        if pd.isna(first["temperature_c"]):
            reasons.append("missing_temperature")
        elif not (0 <= float(first["temperature_c"]) <= 25):
            reasons.append("temperature_outside_0_25C")
        if pd.isna(first["ph"]):
            reasons.append("missing_ph")
        if pd.isna(first["aw"]):
            reasons.append("missing_aw")
        if not first["product_name"]:
            reasons.append("missing_product")
        if reasons:
            exclusions.append({"curve_id": curve_id, "reasons": ";".join(reasons)})

        for _, r in g.iterrows():
            if pd.isna(r["time_hours"]) or pd.isna(r["observed_log_cfu_g"]):
                continue
            obs_rows.append({
                "curve_id": curve_id,
                "time_hours": float(r["time_hours"]),
                "observed_log_cfu_g": float(r["observed_log_cfu_g"]),
                "observed_value_original": r["observed_value_original"],
                "observed_unit_original": normalize_text(r["observed_unit_original"]),
                "qualifier": normalize_text(r["qualifier"]),
            })

    curves = pd.DataFrame(curve_rows)
    observations = pd.DataFrame(obs_rows)
    exclusions_df = pd.DataFrame(exclusions)

    if curves.empty:
        training = pd.DataFrame(columns=[
            "curve_id", "environment_group_id", "product_name", "product_category", "temperature_c", "ph", "aw",
            "initial_inoculum_log_cfu_g", "time_hours", "observed_log_cfu_g"
        ])
    else:
        core = curves.loc[curves["core_complete"]].copy()
        training = observations.merge(
            core[["curve_id", "environment_group_id", "product_name", "product_category", "temperature_c", "ph", "aw", "initial_inoculum_log_cfu_g"]],
            on="curve_id",
            how="inner",
        )
        training = training[[
            "curve_id", "environment_group_id", "product_name", "product_category", "temperature_c", "ph", "aw",
            "initial_inoculum_log_cfu_g", "time_hours", "observed_log_cfu_g"
        ]].sort_values(["curve_id", "time_hours"])

    report = {
        "source_rows_received": int(len(source)),
        "listeria_rows_after_filter": int(len(df)),
        "curves_total": int(len(curves)),
        "observations_total": int(len(observations)),
        "core_complete_curves": int(curves["core_complete"].sum()) if not curves.empty else 0,
        "training_rows": int(len(training)),
        "environment_groups_core": int(training["environment_group_id"].nunique()) if not training.empty else 0,
        "exact_duplicate_observations_removed": int(exact_duplicates_removed),
        "rows_excluded_missing_source_identifier": excluded_missing_ids,
        "curves_with_missing_ph": int(curves["ph"].isna().sum()) if not curves.empty else 0,
        "curves_with_missing_aw": int(curves["aw"].isna().sum()) if not curves.empty else 0,
        "curves_without_time_zero": int((~curves["has_time_zero"]).sum()) if not curves.empty else 0,
    }
    return curves, observations, training, {"summary": report, "exclusions": exclusions_df.to_dict("records")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input file not found: {args.input}")

    source = pd.read_csv(args.input)
    curves, observations, training, qc = build(source)
    args.outdir.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)

    curves.to_csv(args.outdir / "curves.csv", index=False)
    observations.to_csv(args.outdir / "observations.csv", index=False)
    training.to_csv(args.outdir / "training.csv", index=False)
    pd.DataFrame(qc["exclusions"]).to_csv(args.outdir / "exclusions.csv", index=False)
    args.report.write_text(json.dumps(qc["summary"], indent=2), encoding="utf-8")
    print(json.dumps(qc["summary"], indent=2))


if __name__ == "__main__":
    main()
