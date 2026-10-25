# Experimental Python

## Format/Lint code
```sh
uv tool run ruff format
uv tool run ruff check --fix
```

## Run
Delete symlink 
```bash
ls -ld data
unlink data
```
```bash
# Execute at repo root location
export DATA_DIR="$(pwd)/data/"
export OUTPUT_DIR="${DATA_DIR}out/"
# Assume the data is in the separate git repo
ln -s $HOME/experimental-java/data data

uv sync
source .venv/bin/activate
uv run jupyter lab
uv run jupyter lab --allow-root --ip=0.0.0.0 --NotebookApp.allow_origin='*'

uv run python -m src.pc_hardware_analysis.collect_image_urls
uv run python -m src.graph_theory.main
```
http://192.168.64.2:8888/lab?token=<token>
