from __future__ import annotations

import test_project


def test_expose_version():
    assert test_project.__version__
