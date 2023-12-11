from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Sequence

import pytest

from plumbum import local

if TYPE_CHECKING:
    from freezegun.api import FrozenDateTimeFactory
    from pytest_copier import CopierFixture


ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def git_user_name() -> str:
    return "John Doe"


@pytest.fixture(scope="session")
def git_user_email() -> str:
    return "john.doe@local.dev"


@pytest.fixture(scope="session")
def copier_defaults(git_user_name: str, git_user_email: str) -> dict[str, Any]:
    return {
        "project_name": "Test Project",
        "project_description": "A test project",
        "author_fullname": git_user_name,
        "author_email": git_user_email,
        "author_username": "john-doe",
        "copyright_license": "MIT License",
    }


@pytest.fixture(scope="session")
def copier_template_paths() -> Sequence[str]:
    return (
        "template",
        "extensions",
        "copier.yml",
    )


@pytest.fixture
def copier(copier: CopierFixture, monkeypatch: pytest.MonkeyPatch) -> CopierFixture:
    # Ensure runner virtualenv and pdm do not interfere
    for var in "VIRTUAL_ENV", "PDM_PROJECT_ROOT":
        monkeypatch.delenv(var, raising=False)
        monkeypatch.delitem(local.env, var, raising=False)
    monkeypatch.setenv("PDM_IGNORE_ACTIVE_VENV", "1")
    monkeypatch.setitem(local.env, "PDM_IGNORE_ACTIVE_VENV", "1")
    return copier


@pytest.fixture
def test_date(freezer: FrozenDateTimeFactory) -> datetime:
    freezer.move_to("2023-05-14")
    return freezer.time_to_freeze
