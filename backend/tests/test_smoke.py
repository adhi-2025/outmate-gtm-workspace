"""Basic smoke tests for the Outmate backend.

Run with: pytest -q
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_main_module_is_importable():
    main_py = ROOT / "app" / "main.py"
    assert main_py.exists(), "backend/app/main.py is missing"
    spec = importlib.util.spec_from_file_location("outmate_main", main_py)
    assert spec is not None
    assert spec.loader is not None


def test_backend_structure_exists():
    assert (ROOT / "app").is_dir()
    assert (ROOT / "app" / "main.py").is_file()
