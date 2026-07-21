# Experimental DSA Python

## Format/Lint code

```sh
uv tool run ruff format
uv tool run ruff check --fix
```

## Run

```bash
export DATA_DIR="$(pwd)/data"

uv sync
source .venv/bin/activate
uv run jupyter lab

uv run python -m src.graph_theory.main
```
