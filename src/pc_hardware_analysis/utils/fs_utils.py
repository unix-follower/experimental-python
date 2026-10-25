from pathlib import Path


def get_data_dir():
    project_root = Path.cwd().resolve()
    data_dir = project_root / "data"
    if not data_dir.exists():
        project_root = project_root.parent
        raise FileNotFoundError("Could not find data directory")
    return project_root, data_dir
