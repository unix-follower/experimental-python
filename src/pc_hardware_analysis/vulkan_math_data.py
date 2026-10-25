from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def data_dir() -> Path:
    return project_root() / "data"


def _to_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _flatten_feature_flags(features: dict[str, Any]) -> dict[str, int]:
    flattened: dict[str, int] = {}
    for group_name, group_values in features.items():
        if not isinstance(group_values, dict):
            continue
        for feature_name, value in group_values.items():
            if isinstance(value, bool):
                key = f"feat__{group_name}__{feature_name}"
                flattened[key] = int(value)
    return flattened


def _flatten_numeric_properties(
    properties: dict[str, Any], prefix: str = "prop"
) -> dict[str, float]:
    flattened: dict[str, float] = {}
    for key, value in properties.items():
        next_prefix = f"{prefix}__{key}"
        numeric_value = _to_float(value)
        if numeric_value is not None:
            flattened[next_prefix] = numeric_value
            continue
        if isinstance(value, dict):
            flattened.update(_flatten_numeric_properties(value, next_prefix))
    return flattened


def _count_prefix_tokens(values: list[str], prefix: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        token = value.split("_")[1] if value.count("_") >= 2 else "OTHER"
        key = f"{prefix}__{token}"
        counts[key] = counts.get(key, 0) + 1
    return counts


def _infer_vendor_name(*values: Any) -> str | None:
    vendor_tokens = {
        "nvidia": "NVIDIA",
        "amd": "AMD",
        "intel": "Intel",
        "apple": "Apple",
        "asus": "Asus",
        "msi": "MSI",
        "gigabyte": "Gigabyte",
    }
    for value in values:
        if not isinstance(value, str):
            continue
        lowered = value.lower()
        for token, normalized in vendor_tokens.items():
            if token in lowered:
                return normalized
    return None


def normalize_gpu_name(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.lower()
    normalized = normalized.split(" driver ", 1)[0]
    normalized = normalized.split(" on ", 1)[0]
    normalized = re.sub(r"\([^)]*\)", " ", normalized)
    normalized = normalized.replace("-", " ")
    normalized = normalized.replace("geforce", "")
    normalized = normalized.replace("graphics", "")
    normalized = normalized.replace("gpu", "")
    normalized = re.sub(
        r"\b(nvidia|amd|intel|apple|asus|msi|gigabyte|sapphire|powercolor|xfx)\b",
        "",
        normalized,
    )
    normalized = re.sub(
        r"\b(windows|linux|android|macos|mac os|arch|unknown)\b", "", normalized
    )
    normalized = re.sub(r"[^a-z0-9+ ]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _next_profile(data: dict[str, Any], path: Path) -> tuple[str, dict[str, Any]]:
    profiles = data.get("profiles", {})
    if not profiles:
        raise ValueError(
            f"Vulkan profile JSON at {path} does not contain a profiles object"
        )
    profile_key = next(iter(profiles))
    return profile_key, profiles[profile_key]


def flatten_profile(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    profile_key, profile_meta = _next_profile(data, path)
    device = data.get("capabilities", {}).get("device", {})
    features = device.get("features", {})
    properties = device.get("properties", {})
    extensions = data.get("extensions", {})
    formats = data.get("formats", {})
    queue_families = device.get("queueFamiliesProperties", [])
    profile_label = profile_meta.get("label")
    gpu_name = properties.get("VkPhysicalDeviceProperties", {}).get("deviceName")

    flattened = {
        "report_id": path.stem,
        "profile_key": profile_key,
        "profile_label": profile_label,
        "profile_version": profile_meta.get("version"),
        "api_version": profile_meta.get("api-version"),
        "gpu_name": gpu_name,
        "vendor_id": properties.get("VkPhysicalDeviceProperties", {}).get("vendorID"),
        "vendor_name": _infer_vendor_name(profile_label, gpu_name, profile_key),
        "driver_name": properties.get("VkPhysicalDeviceDriverProperties", {}).get(
            "driverName"
        ),
        "driver_info": properties.get("VkPhysicalDeviceDriverProperties", {}).get(
            "driverInfo"
        ),
        "normalized_gpu_name": normalize_gpu_name(gpu_name or profile_label),
        "agg__feature_true_count": 0,
        "agg__extension_count": len(extensions),
        "agg__format_count": len(formats),
        "agg__queue_family_count": len(queue_families),
        "agg__raytracing_feature_count": 0,
        "agg__meshshader_feature_count": 0,
        "agg__descriptor_feature_count": 0,
        "agg__format_support_nonempty_count": 0,
    }

    feature_columns = _flatten_feature_flags(features)
    property_columns = _flatten_numeric_properties(properties)

    flattened.update(feature_columns)
    flattened.update(property_columns)

    flattened["agg__feature_true_count"] = sum(feature_columns.values())
    flattened["agg__raytracing_feature_count"] = sum(
        value for key, value in feature_columns.items() if "ray" in key.lower()
    )
    flattened["agg__meshshader_feature_count"] = sum(
        value for key, value in feature_columns.items() if "mesh" in key.lower()
    )
    flattened["agg__descriptor_feature_count"] = sum(
        value for key, value in feature_columns.items() if "descriptor" in key.lower()
    )

    extension_names = sorted(name for name in extensions if isinstance(name, str))
    flattened.update({f"ext__{name}": 1 for name in extension_names})
    flattened.update(_count_prefix_tokens(extension_names, "agg__extension_family"))

    format_support_nonempty_count = 0
    for format_name, support in formats.items():
        if not isinstance(support, dict):
            continue
        has_support = any(bool(values) for values in support.values())
        flattened[f"fmt__{format_name}"] = int(has_support)
        format_support_nonempty_count += int(has_support)
    flattened["agg__format_support_nonempty_count"] = format_support_nonempty_count

    return flattened


def load_vulkan_feature_frame(profiles_path: Path | None = None) -> pd.DataFrame:
    root = profiles_path or (data_dir() / "vulkan-profiles")
    rows = [flatten_profile(path) for path in sorted(root.glob("*.json"))]
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    return frame.sort_values(["report_id", "profile_key"]).reset_index(drop=True)


def load_gpu_catalog(path: Path | None = None) -> pd.DataFrame:
    catalog_path = path or (data_dir() / "gpu.json")
    with catalog_path.open("r", encoding="utf-8") as handle:
        raw_catalog = json.load(handle)

    rows: list[dict[str, Any]] = []
    for catalog_id, payload in raw_catalog.items():
        row = {"catalog_id": catalog_id, **payload}
        row["catalog_model"] = payload.get("Model")
        row["catalog_vendor"] = payload.get("Vendor")
        row["normalized_gpu_name"] = normalize_gpu_name(payload.get("Model"))
        rows.append(row)
    return pd.DataFrame(rows)


def load_gpu_benchmarks(path: Path | None = None) -> pd.DataFrame:
    benchmark_path = path or (data_dir() / "GPU_UserBenchmarks.csv")
    frame = pd.read_csv(benchmark_path)
    frame.columns = [
        column.strip().lower().replace(" ", "_") for column in frame.columns
    ]
    frame["normalized_gpu_name"] = frame["model"].map(normalize_gpu_name)
    return frame


def attach_catalog_and_benchmarks(
    vulkan_frame: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    catalog = load_gpu_catalog()
    benchmarks = load_gpu_benchmarks()

    catalog_min = catalog[
        ["catalog_id", "catalog_vendor", "catalog_model", "normalized_gpu_name"]
    ].drop_duplicates()
    benchmark_min = benchmarks[
        ["brand", "model", "rank", "benchmark", "samples", "url", "normalized_gpu_name"]
    ].drop_duplicates()

    joined = vulkan_frame.merge(
        catalog_min,
        on="normalized_gpu_name",
        how="left",
        indicator="catalog_match_state",
    )
    joined = joined.merge(
        benchmark_min,
        on="normalized_gpu_name",
        how="left",
        indicator="benchmark_match_state",
    )

    diagnostics = {
        "vulkan_rows": len(vulkan_frame),
        "catalog_matches": int((joined["catalog_match_state"] == "both").sum()),
        "benchmark_matches": int((joined["benchmark_match_state"] == "both").sum()),
        "unmatched_catalog_names": joined.loc[
            joined["catalog_match_state"] != "both",
            ["report_id", "profile_label", "normalized_gpu_name"],
        ].to_dict("records"),
        "unmatched_benchmark_names": joined.loc[
            joined["benchmark_match_state"] != "both",
            ["report_id", "profile_label", "normalized_gpu_name"],
        ].to_dict("records"),
    }
    return joined, diagnostics


def attach_ml_targets(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    enriched["target__benchmark"] = enriched.get("benchmark")
    enriched["target__rank"] = enriched.get("rank")
    enriched["target__surrogate_capability_score"] = (
        enriched["agg__feature_true_count"].fillna(0)
        + 0.5 * enriched["agg__descriptor_feature_count"].fillna(0)
        + 0.5 * enriched["agg__raytracing_feature_count"].fillna(0)
        + 0.25 * enriched["agg__extension_count"].fillna(0)
    )
    capability_threshold = enriched["target__surrogate_capability_score"].median()
    enriched["label__raytracing_capable"] = (
        enriched["agg__raytracing_feature_count"].fillna(0) > 0
    ).astype(int)
    enriched["label__advanced_rendering_capable"] = (
        (enriched["agg__descriptor_feature_count"].fillna(0) > 0)
        & (
            enriched["agg__feature_true_count"].fillna(0)
            >= enriched["agg__feature_true_count"].fillna(0).median()
        )
    ).astype(int)
    enriched["label__high_capability"] = (
        enriched["target__surrogate_capability_score"] >= capability_threshold
    ).astype(int)
    return enriched


def numeric_feature_columns(frame: pd.DataFrame) -> list[str]:
    excluded = {
        "report_id",
        "profile_key",
        "profile_label",
        "api_version",
        "gpu_name",
        "vendor_name",
        "driver_name",
        "driver_info",
        "normalized_gpu_name",
        "catalog_id",
        "catalog_vendor",
        "catalog_model",
        "brand",
        "model",
        "url",
        "catalog_match_state",
        "benchmark_match_state",
        "rank",
        "benchmark",
        "samples",
        "target__benchmark",
        "target__rank",
        "target__surrogate_capability_score",
        "label__raytracing_capable",
        "label__advanced_rendering_capable",
        "label__high_capability",
    }
    numeric_columns = [
        column
        for column in frame.columns
        if column not in excluded and pd.api.types.is_numeric_dtype(frame[column])
    ]
    return sorted(numeric_columns)


def feature_matrix(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    numeric_columns = numeric_feature_columns(frame)
    matrix = frame[numeric_columns].fillna(0)
    nonconstant_columns = [
        column for column in numeric_columns if matrix[column].nunique(dropna=False) > 1
    ]
    return matrix[nonconstant_columns], nonconstant_columns


def load_ml_dataset() -> tuple[pd.DataFrame, dict[str, Any]]:
    vulkan_frame = load_vulkan_feature_frame()
    joined_frame, diagnostics = attach_catalog_and_benchmarks(vulkan_frame)
    ml_frame = attach_ml_targets(joined_frame)
    diagnostics = {
        **diagnostics,
        "benchmark_target_rows": int(ml_frame["target__benchmark"].notna().sum()),
        "raytracing_positive_rows": int(ml_frame["label__raytracing_capable"].sum()),
        "advanced_rendering_positive_rows": int(
            ml_frame["label__advanced_rendering_capable"].sum()
        ),
        "high_capability_positive_rows": int(ml_frame["label__high_capability"].sum()),
    }
    return ml_frame, diagnostics
