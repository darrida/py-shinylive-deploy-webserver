# ruff: noqa: S101 S603 S607
import shutil
from pathlib import Path

import pytest
from shinylive_deploy.process.base import WindowsPaths


def reset_local_dirs():
    original_copy = Path(__file__).resolve().parent / "sample_files" / "windows_path_app.json"
    app_js_path = Path(__file__).resolve().parent / "sample_files" / "temp-app.json"
    if app_js_path.exists():
        app_js_path.unlink()
    shutil.copy(original_copy, app_js_path)


@pytest.fixture()
def dirs_session():
    reset_local_dirs()
    yield
    reset_local_dirs()


def test_fix_windows_paths(dirs_session):
    # original_copy = Path(__file__).resolve().parent / "sample_files" / "app.json"
    app_js_path = Path(__file__).resolve().parent / "sample_files" / "temp-app.json"
    # shutil.copy(original_copy, app_js_path)

    with open(app_js_path) as f:
        first_check = f.read()
    results = WindowsPaths._find_impacted(first_check)
    assert results

    # Run tested operation
    WindowsPaths.workaround(app_js_path)

    # Check that no path issues are found
    with open(app_js_path) as f:
        second_check = f.read()
    results = WindowsPaths._find_impacted(second_check)
    assert not results
