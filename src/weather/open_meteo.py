from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "open-meteo"


@dataclass(frozen=True)
class OpenMeteoDataset:
    path: Path
    slug: str
    kind: str
    row_count: int
    columns: tuple[str, ...]
    time_key: str | None


@dataclass(frozen=True)
class HourlyTable:
    timestamps: tuple[str, ...]
    columns: dict[str, tuple[Any, ...]]
    sources: dict[str, str]

    @property
    def row_count(self) -> int:
        return len(self.timestamps)

    @property
    def column_count(self) -> int:
        return len(self.columns)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _dataset_slug(path: Path) -> str:
    stem = path.stem
    if stem.startswith("gomel-"):
        stem = stem.removeprefix("gomel-")

    suffix = "-2020-01-01-2026-05-30"
    if stem.endswith(suffix):
        stem = stem[: -len(suffix)]

    return stem.replace("-", "_")


def _classify_payload(payload: dict[str, Any]) -> tuple[str, str | None]:
    if "hourly" in payload:
        return "hourly", "time"
    if "daily" in payload:
        return "daily", "time"
    if "current" in payload:
        return "current", "time"
    if all(key in payload for key in ("latitude", "longitude", "timezone")):
        return "metadata", None
    raise ValueError("Unsupported Open-Meteo payload; expected hourly, daily, current, or metadata-only sections")


def _row_count(section: Any, time_key: str | None) -> int:
    if time_key is None:
        return 0

    if isinstance(section, dict):
        time_value = section.get(time_key)
        if isinstance(time_value, list):
            return len(time_value)
        if time_value is not None:
            return 1

    return 0


def list_datasets(data_dir: Path = DEFAULT_DATA_DIR) -> list[OpenMeteoDataset]:
    datasets: list[OpenMeteoDataset] = []

    for path in sorted(data_dir.glob("*.json")):
        payload = _load_json(path)
        kind, time_key = _classify_payload(payload)
        section = payload.get(kind, {}) if kind != "metadata" else {}
        columns = tuple(key for key in section.keys() if key != "time") if isinstance(section, dict) else ()
        datasets.append(
            OpenMeteoDataset(
                path=path,
                slug=_dataset_slug(path),
                kind=kind,
                row_count=_row_count(section, time_key),
                columns=columns,
                time_key=time_key,
            )
        )

    return datasets


def build_hourly_table(data_dir: Path = DEFAULT_DATA_DIR) -> HourlyTable:
    datasets = [dataset for dataset in list_datasets(data_dir) if dataset.kind == "hourly"]
    if not datasets:
        raise ValueError(f"No hourly datasets found in {data_dir}")

    timestamps: tuple[str, ...] | None = None
    columns: dict[str, tuple[Any, ...]] = {}
    sources: dict[str, str] = {}

    for dataset in datasets:
        payload = _load_json(dataset.path)
        section = payload["hourly"]
        current_times = tuple(section["time"])

        if timestamps is None:
            timestamps = current_times
        elif current_times != timestamps:
            raise ValueError(
                f"Timestamp mismatch for {dataset.path.name}: expected shared hourly index"
            )

        for column_name, values in section.items():
            if column_name == "time":
                continue
            if len(values) != len(current_times):
                raise ValueError(
                    f"Length mismatch for {dataset.path.name}:{column_name}; expected {len(current_times)} rows"
                )

            qualified_name = f"{dataset.slug}__{column_name}"
            columns[qualified_name] = tuple(values)
            sources[qualified_name] = dataset.path.name

    if timestamps is None:
        raise ValueError(f"No hourly timestamps found in {data_dir}")

    return HourlyTable(timestamps=timestamps, columns=columns, sources=sources)


def summarize_inventory(data_dir: Path = DEFAULT_DATA_DIR) -> dict[str, Any]:
    datasets = list_datasets(data_dir)
    counts: dict[str, int] = {"hourly": 0, "daily": 0, "current": 0, "metadata": 0}

    for dataset in datasets:
        counts[dataset.kind] = counts.get(dataset.kind, 0) + 1

    return {
        "data_dir": str(data_dir),
        "dataset_count": len(datasets),
        "counts": counts,
        "datasets": [
            {
                "file": dataset.path.name,
                "slug": dataset.slug,
                "kind": dataset.kind,
                "rows": dataset.row_count,
                "column_count": len(dataset.columns),
            }
            for dataset in datasets
        ],
    }


def summarize_hourly_table(data_dir: Path = DEFAULT_DATA_DIR) -> dict[str, Any]:
    table = build_hourly_table(data_dir)

    return {
        "data_dir": str(data_dir),
        "rows": table.row_count,
        "columns": table.column_count,
        "start": table.timestamps[0] if table.timestamps else None,
        "end": table.timestamps[-1] if table.timestamps else None,
        "sources": sorted(set(table.sources.values())),
        "sample_columns": list(table.columns.keys())[:10],
    }


def export_hourly_csv(data_dir: Path = DEFAULT_DATA_DIR, output_path: Path | None = None) -> dict[str, Any]:
    table = build_hourly_table(data_dir)
    destination = output_path or data_dir.parent / "derived" / "canonical_hourly.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)

    ordered_columns = sorted(table.columns.keys())
    fieldnames = [
        "timestamp",
        "year",
        "month",
        "day",
        "hour",
        "day_of_year",
        "weekday",
        *ordered_columns,
    ]

    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for index, timestamp in enumerate(table.timestamps):
            dt = datetime.fromisoformat(timestamp)
            row: dict[str, Any] = {
                "timestamp": timestamp,
                "year": dt.year,
                "month": dt.month,
                "day": dt.day,
                "hour": dt.hour,
                "day_of_year": dt.timetuple().tm_yday,
                "weekday": dt.weekday(),
            }

            for column_name in ordered_columns:
                row[column_name] = table.columns[column_name][index]

            writer.writerow(row)

    return {
        "output": str(destination),
        "rows": table.row_count,
        "columns": len(fieldnames),
        "data_columns": table.column_count,
    }
