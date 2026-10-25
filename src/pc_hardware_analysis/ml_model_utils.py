from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import tensorflow as tf
import torch
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass
class ModelRun:
    name: str
    framework: str
    task: str
    metrics: dict[str, float]
    predictions: np.ndarray
    details: dict[str, Any]


def set_seed(seed: int = 7) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    tf.keras.utils.set_random_seed(seed)


def reduce_feature_set(X: pd.DataFrame, max_features: int = 32) -> pd.DataFrame:
    if X.shape[1] <= max_features:
        return X.copy()
    variances = X.var(axis=0).sort_values(ascending=False)
    selected = variances.head(max_features).index.to_list()
    return X[selected].copy()


def regression_target(frame: pd.DataFrame) -> tuple[pd.Series, str]:
    if frame["target__benchmark"].notna().sum() >= 2:
        return frame["target__benchmark"].astype(float), "target__benchmark"
    return frame["target__surrogate_capability_score"].astype(
        float
    ), "target__surrogate_capability_score"


def classification_target(frame: pd.DataFrame) -> tuple[pd.Series, str]:
    for column in [
        "label__high_capability",
        "label__advanced_rendering_capable",
        "label__raytracing_capable",
    ]:
        values = frame[column].dropna().unique()
        if len(values) >= 2:
            return frame[column].astype(int), column
    return frame["label__high_capability"].astype(int), "label__high_capability"


def _regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def _classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
    }


def run_sklearn_regression_models(
    X: pd.DataFrame, y: pd.Series, seed: int = 7
) -> list[ModelRun]:
    models = {
        "ridge": Pipeline(
            [("scale", StandardScaler()), ("model", Ridge(alpha=1.0))], memory=None
        ),
        "random_forest": RandomForestRegressor(
            n_estimators=50,
            max_features="sqrt",
            min_samples_leaf=1,
            random_state=seed,
        ),
        "gradient_boosting": GradientBoostingRegressor(
            learning_rate=0.05, random_state=seed
        ),
    }
    runs: list[ModelRun] = []
    for name, model in models.items():
        model.fit(X, y)
        predictions = np.asarray(model.predict(X), dtype=float)
        runs.append(
            ModelRun(
                name=name,
                framework="scikit-learn",
                task="regression",
                metrics=_regression_metrics(y.to_numpy(dtype=float), predictions),
                predictions=predictions,
                details={"feature_count": int(X.shape[1])},
            )
        )
    return runs


def run_torch_regressor(
    X: pd.DataFrame, y: pd.Series, seed: int = 7, epochs: int = 250
) -> ModelRun:
    set_seed(seed)
    scaled_x = StandardScaler().fit_transform(X)
    x_tensor = torch.tensor(scaled_x, dtype=torch.float32)
    y_tensor = torch.tensor(
        y.to_numpy(dtype=np.float32).reshape(-1, 1), dtype=torch.float32
    )

    model = torch.nn.Sequential(
        torch.nn.Linear(x_tensor.shape[1], min(16, max(4, x_tensor.shape[1]))),
        torch.nn.ReLU(),
        torch.nn.Linear(min(16, max(4, x_tensor.shape[1])), 1),
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=0.0)
    loss_fn = torch.nn.MSELoss()
    loss_history: list[float] = []

    for _ in range(epochs):
        optimizer.zero_grad()
        preds = model(x_tensor)
        loss = loss_fn(preds, y_tensor)
        loss.backward()
        optimizer.step()
        loss_history.append(float(loss.detach().cpu().item()))

    predictions = model(x_tensor).detach().cpu().numpy().reshape(-1)
    return ModelRun(
        name="dense_regressor",
        framework="PyTorch",
        task="regression",
        metrics=_regression_metrics(y.to_numpy(dtype=float), predictions),
        predictions=predictions,
        details={"loss_history": loss_history},
    )


def run_tensorflow_regressor(
    X: pd.DataFrame, y: pd.Series, seed: int = 7, epochs: int = 250
) -> ModelRun:
    set_seed(seed)
    scaler = StandardScaler()
    scaled_x = scaler.fit_transform(X)
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(scaled_x.shape[1],)),
            tf.keras.layers.Dense(
                min(16, max(4, scaled_x.shape[1])), activation="relu"
            ),
            tf.keras.layers.Dense(1),
        ]
    )
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.01), loss="mse")
    history = model.fit(
        scaled_x, y.to_numpy(dtype=np.float32), epochs=epochs, verbose=0
    )
    predictions = model.predict(scaled_x, verbose=0).reshape(-1)
    return ModelRun(
        name="keras_dense_regressor",
        framework="TensorFlow",
        task="regression",
        metrics=_regression_metrics(y.to_numpy(dtype=float), predictions),
        predictions=predictions,
        details={"loss_history": history.history["loss"]},
    )


def run_sklearn_classification_models(
    X: pd.DataFrame, y: pd.Series, seed: int = 7
) -> list[ModelRun]:
    models = {
        "logistic_regression": Pipeline(
            [
                ("scale", StandardScaler()),
                ("model", LogisticRegression(random_state=seed, max_iter=1000)),
            ],
            memory=None,
        ),
        "random_forest_classifier": RandomForestClassifier(
            n_estimators=50,
            max_features="sqrt",
            min_samples_leaf=1,
            random_state=seed,
        ),
        "gradient_boosting_classifier": GradientBoostingClassifier(
            learning_rate=0.05, random_state=seed
        ),
    }
    runs: list[ModelRun] = []
    for name, model in models.items():
        model.fit(X, y)
        predictions = np.asarray(model.predict(X), dtype=int)
        runs.append(
            ModelRun(
                name=name,
                framework="scikit-learn",
                task="classification",
                metrics=_classification_metrics(y.to_numpy(dtype=int), predictions),
                predictions=predictions,
                details={"feature_count": int(X.shape[1])},
            )
        )
    return runs


def run_tensorflow_classifier(
    X: pd.DataFrame, y: pd.Series, seed: int = 7, epochs: int = 250
) -> ModelRun:
    set_seed(seed)
    scaler = StandardScaler()
    scaled_x = scaler.fit_transform(X)
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(scaled_x.shape[1],)),
            tf.keras.layers.Dense(
                min(16, max(4, scaled_x.shape[1])), activation="relu"
            ),
            tf.keras.layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
        loss="binary_crossentropy",
    )
    history = model.fit(
        scaled_x, y.to_numpy(dtype=np.float32), epochs=epochs, verbose=0
    )
    probabilities = model.predict(scaled_x, verbose=0).reshape(-1)
    predictions = (probabilities >= 0.5).astype(int)
    return ModelRun(
        name="keras_dense_classifier",
        framework="TensorFlow",
        task="classification",
        metrics=_classification_metrics(y.to_numpy(dtype=int), predictions),
        predictions=predictions,
        details={
            "loss_history": history.history["loss"],
            "probabilities": probabilities.tolist(),
        },
    )


def model_runs_frame(runs: list[ModelRun]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for run in runs:
        row = {
            "framework": run.framework,
            "model": run.name,
            **run.metrics,
        }
        rows.append(row)
    return pd.DataFrame(rows)
