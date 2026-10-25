# Copilot Instructions

Experiments with data structures, algorithms, graph theory, geospatial analysis and PC/GPU hardware analysis
(Vulkan profiles, math and ML) in Python 3.13 / uv (networkx, geopandas, pandas, numpy, scipy, scikit-learn, torch,
tensorflow, matplotlib, seaborn; pytest for tests). Dependencies live in `pyproject.toml`.

## Layout

- `src/graph_theory/` – `analysis.ipynb` and `utils/ripe_parser.py` (RIPE Atlas traceroute NDJSON → networkx graph; argparse CLI).
- `src/geospatial/by_gomel_analysis/analysis.ipynb` – geospatial analysis of Gomel (Belarus).
- `src/pc_hardware_analysis/` – GPU/PC component analysis (moved from another repo):
  - notebooks: `algebra_vulkan_profiles`, `calculus_vulkan_performance`, `multivariable_vulkan_optimization`,
    `binary_classification`, `ml_*` (data quality, feature engineering, regression/classification variants,
    unsupervised, evaluation/interpretability, GPU-selection optimization), `pytorch_image_classification`.
  - `ml_model_utils.py` – shared ML helpers (`set_seed`, `ModelRun`, `run_*` model runners, `model_runs_frame`).
  - `vulkan_math_data.py` – Vulkan profile / GPU catalog / benchmark loaders and feature matrix builders.
  - `collect_image_urls.py` – image URL collection script (aiohttp + beautifulsoup4).
  - `utils/fs_utils.py` – data-dir lookup helper.
- `src/config/` (logging settings/`logging.json`), `src/constants.py`.
- `tests/` mirrors `src/` (e.g. `tests/graph_theory/test_ripe_parser.py`); pytest uses `pythonpath = ["src"]`.
- `data/` holds input datasets (not tracked, except docs/scripts; may be a symlink to an external datasets dir). Graph/geospatial
  notebooks read the `DATA_DIR` env var; `OUTPUT_DIR` is used for outputs. `pc_hardware_analysis` helpers
  (`vulkan_math_data.data_dir()`, `utils/fs_utils.get_data_dir()`) resolve `data/` relative to the repo/cwd instead.

## Commands (run from the repo root)

```bash
export DATA_DIR="$(pwd)/data" OUTPUT_DIR="$(pwd)/out"
uv sync --locked
uv tool run ruff format
uv tool run ruff check --fix      # CI runs `uv tool run ruff check`
uv run pytest
uv build
uv run jupyter lab
uv run python -m src.graph_theory.utils.ripe_parser <file.ndjson>
uv run python -m src.pc_hardware_analysis.collect_image_urls
```

Remote/VM Jupyter only: `uv run jupyter lab --allow-root --ip=0.0.0.0` (see `README.md`); never commit tokens or URLs with tokens.

## CI

`.github/workflows/build.yaml` runs on every PR (and manual dispatch): `uv sync --locked`, `uv tool run ruff check`, `uv run pytest`, `uv build`.

## Code Placement

- Most exploratory work lives in Jupyter notebooks under `src/`; reusable logic lives in regular Python modules.
- Put reusable data-loading, feature-engineering, modeling, and evaluation logic in modules next to the notebooks
  (e.g. `src/pc_hardware_analysis/*.py`, `src/graph_theory/utils/`), not directly in notebooks.
- Keep notebooks focused on analysis flow, visualization, and interpretation.
- Avoid moving large analytical workflows into CLI/script entrypoints unless the task is explicitly to build one.
- Add tests for new reusable logic under `tests/<package>/` (e.g. `tests/pc_hardware_analysis/`).

## Python Style

- Follow the existing simple Python style: small functions, explicit control flow, `snake_case`, and standard-library typing.
- Prefer type hints on new functions and dataclasses for structured results.
- Keep implementations straightforward; avoid unnecessary abstractions, framework layers, or metaprogramming.
- Reuse existing helpers when possible, especially `set_seed`, `ModelRun` and `model_runs_frame` in `src/pc_hardware_analysis/ml_model_utils.py`.

## Data and File Handling

- Reuse the existing loaders in `vulkan_math_data.py` for Vulkan/GPU datasets instead of re-parsing files in notebooks.
- Treat files in `data/` as source data unless the task explicitly requires generating derived artifacts.
- Do not overwrite raw CSV, JSON, or SQL schema files unless the change clearly belongs to the dataset itself.
- When adding derived outputs, keep them clearly named and separate from raw source files.
- Use stable, reproducible path handling and assume code runs from the repository root.

## Analysis and ML Guidance

- Prefer `pandas` DataFrames for tabular transformations and keep feature engineering explicit and readable.
- Preserve reproducibility for ML code by setting random seeds when training models.
- Avoid data leakage: do not fit scalers or models on target information outside the intended training scope.
- Report clear metrics for the task type, following the existing pattern of structured metric dictionaries and result tables.
- Keep model-comparison code readable and side-effect-light; prefer returning data structures over printing intermediate state.

## Notebook Guidance

- If notebook logic becomes reusable or repeated, factor it into a Python module under `src/`.
- Keep notebook cells deterministic where practical and avoid hidden state dependencies.
- Prefer concise markdown explanations tied directly to the analysis being performed.

## Dependency and Change Discipline

- Do not introduce new dependencies unless they are necessary for the task; if you do, update `pyproject.toml` consistently.
- Keep changes focused on the requested task and avoid unrelated refactors.
- Preserve existing file organization and naming patterns unless there is a clear reason to change them.

## When Generating Code

- Favor code that is easy to inspect in a research workflow over code optimized for abstraction or premature generalization.
- For modeling utilities, prefer functions that accept DataFrames or Series and return plain Python or pandas objects.
- For visualizations, use `matplotlib` or `seaborn` unless the task explicitly calls for something else.
- When uncertain, optimize for reproducibility, transparency, and minimal surprise.
