import pytest
from mecwaypy.cli import solve_multi, handle_result, solve, MECWAY_EXE_PATH
from multiprocessing.pool import Pool
from pathlib import Path
import subprocess


@pytest.fixture
def apply_async_result():
    return []


@pytest.fixture
def run_result():
    return []


@pytest.fixture
def mock_appy_async(apply_async_result):
    def apply_async(self, solve, args, kwds, callback):
        apply_async_result.extend([solve, args, kwds, callback])
    return apply_async


@pytest.fixture
def mock_glob():
    def glob(*args, **kwargs):
        yield Path("foo.liml")
    return glob


@pytest.fixture
def mock_run(run_result):
    def run(args, **kwargs):
        run_result.extend([args, kwargs])
    return run


@pytest.fixture
def patched_apply_async(monkeypatch, mock_appy_async):
    monkeypatch.setattr(Pool, "apply_async", mock_appy_async)


@pytest.fixture
def patched_glob(monkeypatch, mock_glob):
    monkeypatch.setattr(Path, "glob", mock_glob)


@pytest.fixture
def patched_run(monkeypatch, mock_run):
    monkeypatch.setattr(subprocess, "run", mock_run)


@pytest.mark.parametrize("path_or_paths, glob", [
    ("foo.liml", None),
    (Path("foo.liml"), None),
    ("", "foo.liml"),
])
def test_solve_multi(path_or_paths, glob, patched_apply_async, apply_async_result, patched_glob):
    kwds = dict(glob=glob, window=True)
    solve_multi(path_or_paths, **kwds)
    kwds.pop("glob")
    assert apply_async_result == [solve, [Path("foo.liml")], kwds, handle_result]


@pytest.mark.parametrize("liml_path", [
    "foo.liml",
    Path("foo.liml")
])
def test_solve(liml_path, patched_run, run_result):
    solve(liml_path)
    args = [f'{MECWAY_EXE_PATH!s}', f'{liml_path!s}', "solve"]
    assert run_result == [args, {}]
