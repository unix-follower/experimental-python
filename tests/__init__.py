import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
print(f"PROJECT_ROOT: {PROJECT_ROOT}")

SRC_ROOT = PROJECT_ROOT / "src"
print(f"SRC_ROOT: {SRC_ROOT}")

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
print(f"sys.path: {sys.path}")
