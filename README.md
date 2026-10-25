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

## MoleculeNet Analysis
```bash
export DB_URL='postgresql+psycopg_async://chemist:chemist@192.168.64.2:5432/moleculenet?options=-csearch_path%3Dmoleculenet,public'
```

The `data/` directory contains MoleculeNet-style benchmark datasets spanning:
- binary classification: BBBP, ClinTox, HIV
- regression: Delaney, Lipophilicity, SAMPL, BACE
- multitask or multilabel classification: Tox21, SIDER, MUV, ToxCast
- quantum-property regression: QM8, QM9, `qm7b.mat`

### Current Baselines

The first validated benchmark is the scikit-learn BBBP baseline using character n-gram TF-IDF plus logistic regression.

Validation metrics on the current split:
- accuracy: `0.8762`
- F1: `0.9159`
- ROC AUC: `0.9471`

The first regression benchmark is Delaney ESOL using tabular descriptors.

Validation metrics on the current split:
- ridge: RMSE `0.8650`, MAE `0.6414`, R2 `0.8515`
- random forest: RMSE `0.6137`, MAE `0.4316`, R2 `0.9252`
- PyTorch MLP: RMSE `0.6656`, MAE `0.4771`, R2 `0.9120`
- TensorFlow MLP: RMSE `0.6523`, MAE `0.4588`, R2 `0.9155`

The regression extension to Lipophilicity uses the same split contract with SMILES-text features.

Validation metrics on the current split:
- ridge: RMSE `0.8099`, MAE `0.6340`, R2 `0.5520`
- elasticnet: RMSE `0.8493`, MAE `0.6650`, R2 `0.5074`

Cross-framework BBBP validation metrics:
- scikit-learn: accuracy `0.8762`, F1 `0.9159`, ROC AUC `0.9471`
- PyTorch: accuracy `0.7296`, F1 `0.8019`, ROC AUC `0.8103`
- TensorFlow: accuracy `0.8241`, F1 `0.8916`, ROC AUC `0.8546`

### Design Notes

- Use `mol_id`, `CID`, `CMPD_CHEMBLID`, or `Compound ID` as natural keys when available.
- Treat sparse multitask labels as nullable targets.
- Normalize QM8 duplicate headers before any modeling work.
- Use framework-matched task definitions so comparisons are meaningful.

## Weather Analysis

Initial implementation now covers Open-Meteo file discovery, schema classification, canonical hourly alignment, and CSV export from the current Gomel dataset under `data/in/open-meteo`.

### Commands

Run from the project root.

```bash
uv run python src/weather/main.py inventory
uv run python src/weather/main.py hourly-summary
uv run python src/weather/main.py export-hourly-csv
```

Optional export location:

```bash
uv run python src/main.py export-hourly-csv --output data/out/weather/derived/gomel-hourly.csv
```

Notebook workflow:

```bash
uv run jupyter notebook src/weather/01_weather_forecasting_clustering_anomaly.ipynb
uv run jupyter notebook src/weather/02_aqi_prediction.ipynb
uv run jupyter notebook src/weather/03_pytorch_sequence_aqi_forecasting.ipynb
uv run jupyter notebook src/weather/04_pytorch_tabular_temperature_forecasting.ipynb
uv run jupyter notebook src/weather/05_pytorch_cnn_wind_anomaly_detection.ipynb
uv run jupyter notebook src/weather/06_pytorch_transformer_representation_learning.ipynb
uv run jupyter notebook src/weather/07_pytorch_autoencoder_unsupervised.ipynb
```

### Current behavior

- Inventories all surviving JSON files in `data/in/open-meteo`
- Separates hourly, daily, current, and metadata-only payloads
- Builds one canonical hourly table from the existing hourly datasets
- Excludes the deleted legacy single-variable file from all assumptions
- Keeps flood data out of the hourly export because it is daily-resolution

### Current dataset summary

- 12 hourly files
- 1 daily flood file
- 1 current-conditions snapshot file
- 1 metadata-only file
- 56,208 hourly timestamps from 2020-01-01T00:00 through 2026-05-30T23:00
- 151 aligned hourly data columns before calendar features

### Next implementation slices

- Add a reusable analysis package structure under `src/`
- Materialize a daily table for flood modeling
- Add feature engineering for lagged variables, derivatives, and rolling windows
- Add more baseline notebooks or scripts for regression, forecasting, and anomaly detection
- Add PyTorch sequence and deep-learning baselines next to the sklearn notebooks
