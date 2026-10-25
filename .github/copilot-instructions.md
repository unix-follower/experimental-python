# Copilot Instructions

Experiments with data structures, algorithms and graph theory in Python 3.13 / uv
(networkx, geopandas, pandas, scipy, matplotlib; pytest for tests).

## Layout

- `src/graph_theory/` – `analysis.ipynb` and `utils/ripe_parser.py` (RIPE Atlas traceroute NDJSON → networkx graph; argparse CLI).
- `src/geospatial/by_gomel/analysis.ipynb` – geospatial analysis of Gomel (Belarus).
- `src/config/` (logging settings/`logging.json`), `src/constants.py`.
- `tests/` mirrors `src/` (e.g. `tests/graph_theory/test_ripe_parser.py`); pytest uses `pythonpath = ["src"]`.
- `data/` holds input datasets (not tracked, except docs/scripts). Notebooks read the `DATA_DIR` env var; `OUTPUT_DIR` is used for outputs.

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
```

## CI

`.github/workflows/build.yaml` runs on every PR (and manual dispatch): `uv sync --locked`, `uv tool run ruff check`, `uv run pytest`, `uv build`.
