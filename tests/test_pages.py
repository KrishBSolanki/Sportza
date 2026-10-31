"""Integration test running all Streamlit dashboard pages via AppTest."""
import glob
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

ROOT_DIR = Path(__file__).resolve().parent.parent
PAGES = [str(ROOT_DIR / "app.py")] + sorted(str(p) for p in ROOT_DIR.glob("pages/*.py"))


@pytest.mark.parametrize("page_path", PAGES)
def test_streamlit_page_renders_without_errors(page_path: str):
    """Verify that each page compiles and runs without unhandled exceptions."""
    path = Path(page_path)
    assert path.exists(), f"Page file {path} not found"
    at = AppTest.from_file(str(path), default_timeout=30)
    at.run()
    assert not at.exception, f"Errors in {path.name}: {[e.message for e in at.exception]}"
