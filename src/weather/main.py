from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_meteo import (
    DEFAULT_DATA_DIR,
    export_hourly_csv,
    summarize_hourly_table,
    summarize_inventory,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Weather analysis project utilities")
    parser.add_argument(
        "command",
        choices=("inventory", "hourly-summary", "export-hourly-csv"),
        help="Inventory Open-Meteo files, summarize the canonical hourly table, or export it as CSV",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory containing Open-Meteo JSON files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path for export-hourly-csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "inventory":
        payload = summarize_inventory(args.data_dir)
    elif args.command == "hourly-summary":
        payload = summarize_hourly_table(args.data_dir)
    else:
        payload = export_hourly_csv(args.data_dir, args.output)

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
