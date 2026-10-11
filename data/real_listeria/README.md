# Iapetus real Listeria dataset

This directory defines the canonical real-data release for the first production-oriented Iapetus Listeria model.

## Scope

Organism: *Listeria monocytogenes* only.

Model-facing inputs:

- `product_name`
- `product_category`
- `temperature_c`
- `ph`
- `aw`
- `initial_inoculum_log_cfu_g`
- `time_hours`

Target:

- `observed_log_cfu_g`

The canonical dataset retains additional provenance and QC columns, but they are not model features.

## Inclusion rules for the core dataset

A curve is eligible for the core training release when:

1. the organism is *Listeria monocytogenes*;
2. the source is a traceable experimental observation (ComBase record or peer-reviewed/open repository dataset);
3. the curve has a measurement at `time_hours == 0` so the initial inoculum can be determined directly;
4. the curve has at least 5 timepoints for the Hiura-2021-compatible cohort, or at least 4 timepoints for later expansion cohorts if explicitly tagged;
5. temperature is constant and between 0 and 25 C for the initial benchmark cohort;
6. observed counts can be expressed as log10 CFU/g (or an equivalent unit whose conversion is explicitly documented);
7. product/medium identity is known;
8. the curve is not a duplicate of another retained source record.

For the first strict Iapetus release, rows missing pH or aW are retained in the canonical source table but are excluded from the `core_complete` training subset. This preserves source truth without silently imputing scientific measurements.

## Canonical tables

### `curves.csv`

One row per experimental curve.

Required fields:

- `curve_id`
- `source_key`
- `source_record_id`
- `source_doi`
- `organism`
- `product_name_original`
- `product_name`
- `product_category_original`
- `product_category`
- `temperature_c`
- `ph`
- `aw`
- `initial_inoculum_log_cfu_g`
- `n_timepoints`
- `has_time_zero`
- `core_complete`
- `environment_group_id`
- `provenance_url`

### `observations.csv`

One row per measured timepoint.

Required fields:

- `curve_id`
- `time_hours`
- `observed_log_cfu_g`
- `observed_value_original`
- `observed_unit_original`
- `qualifier`

### `training.csv`

Generated table used by the tabular ML models. It contains only the model inputs, target, and grouping identifiers required for leakage-safe splitting.

## Provenance policy

No model row is allowed to exist without a traceable `curve_id`, `source_key`, and source record/publication identifier. Missing pH/aW values stay missing in the canonical tables. Values inferred from literature defaults must be stored separately and must never overwrite the reported source value.

## Leakage policy

Never split individual timepoints randomly. All observations belonging to a `curve_id` stay in the same split. The preferred benchmark split groups identical environmental conditions (`temperature_c`, `ph`, `aw`, `product_category`, `product_name`) into a shared `environment_group_id` so replicate curves cannot leak across train/test.

## Initial benchmark

The first reproducible benchmark is based on Hiura, Koseki & Koyama (2021), DOI `10.1038/s41598-021-90164-z`, which reports 2,531 ComBase Listeria record IDs, 27,059 viable-count observations and 1,007 grouped environmental conditions.

The two publisher supplementary index files have now been acquired and verified separately from the model data: S1 contains exactly 2,531 unique ComBase Record IDs and S2 contains exactly 112 unique food/medium names. Their checksums and row counts are recorded in `metadata/hiura_2021_supplement_manifest.json`. S2 is a vocabulary, not a Record-ID-to-food mapping; reconstruction of the actual curves still requires the corresponding ComBase Browser exports containing record metadata and time/count observations.

Additional cohorts should be tracked in `metadata/source_manifest.csv` and added only after deduplication against the benchmark cohort.
