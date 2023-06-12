from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

from plumbum import local

if TYPE_CHECKING:
    from .conftest import TplHelper

ANSWERS_FILE = ".copier-answers.yml"

pdm = local["pdm"]


def test_apply_default(tpl: TplHelper, shared_datadir: Path):
    tpl.copy()
    tpl.assert_dst_equal(shared_datadir / "defaults")
    tpl.assert_pdm_scripts("test", "lint", "doc")


def test_apply_gitlab(tpl: TplHelper, shared_datadir: Path):
    tpl.copy(repository_provider="gitlab.com")
    tpl.assert_dst_equal(shared_datadir / "gitlab")
    tpl.assert_pdm_scripts("test", "lint", "doc")
