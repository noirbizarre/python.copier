from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from pytest_copier import CopierFixture


pytestmark = pytest.mark.usefixtures("test_date")

IGNORED = [
    "pdm.lock",
    ".pdm-build",
    ".pdm-python",
    "*.egg-info",
    ".ruff_cache",
    ".venv",
    "__pypackages__",
    "VERSION",
]


CASES: dict[str, dict[str, Any]] = {
    "defaults": {},
    "with-docs": {"has_docs": True},
    "no-src": {"use_src": False},
    "library": {"is_lib": True},
    "gitlab": {"repository_provider": "gitlab.com"},
}


@pytest.mark.parametrize(
    "name,data", [pytest.param(name, data, id=name) for name, data in CASES.items()]
)
def test_apply(
    copier: CopierFixture,
    shared_datadir: Path,
    data: dict[str, Any],
    name: str,
):
    project = copier.copy(**data)
    project.assert_answers(shared_datadir / name)
    project.assert_equal(shared_datadir / name, ignore=IGNORED)

    assert (project / "pdm.lock").exists()
    project.run("pdm test")
    project.run("pdm lint")
