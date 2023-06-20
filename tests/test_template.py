from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, Any


import pytest

if TYPE_CHECKING:
    from freezegun.api import FrozenDateTimeFactory
    from .conftest import CopierHelper

ANSWERS_FILE = ".copier-answers.yml"
TEST_DATE = "2023-05-14"


CASES: dict[str, dict[str, Any]] = {
    "defaults": {},
    "with-docs": {"has_docs": True},
    "no-src": {"use_src": False},
    "library": {"is_lib": True},
    "gitlab": dict(repository_provider="gitlab.com"),
}


@pytest.mark.parametrize(
    "name,data", [pytest.param(name, data, id=name) for name, data in CASES.items()]
)
def test_apply(
    copier: CopierHelper, shared_datadir: Path, data: dict[str, Any], name: str, freezer: FrozenDateTimeFactory
):
    freezer.move_to(TEST_DATE)
    copier.copy(**data)
    copier.assert_answers(shared_datadir / name)
    copier.assert_dst_equal(shared_datadir / name)
    copier.assert_pdm_scripts("test", "lint", "doc")
