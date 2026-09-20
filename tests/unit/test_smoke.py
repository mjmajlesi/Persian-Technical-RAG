"""Smoke test: the src/ package tree imports cleanly (T005)."""

import importlib


def test_src_packages_import():
    for pkg in ("src", "src.ingest", "src.index", "src.qa", "src.eval", "src.web"):
        assert importlib.import_module(pkg) is not None
