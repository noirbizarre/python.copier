from __future__ import annotations

from dataclasses import dataclass
import filecmp
from io import StringIO
import os
from pathlib import Path
import shlex
from shutil import copy, copytree
import shutil
from sys import stdout
import sys
from typing import TYPE_CHECKING, Any, Iterator, Sequence

# from plumbum import local
# from subprocess import run
import yaml
import subprocess

import icdiff
from copier.main import run_copy, run_update

import pytest

from pytest_gitconfig.plugin import GitConfig
from pytest_dir_equal import assert_dir_equal, DEFAULT_IGNORES

from _pytest._code.code import TerminalRepr
from _pytest._io import TerminalWriter, get_terminal_width

if TYPE_CHECKING:
    from pytest_dir_equal import DirDiff


ROOT = Path(__file__).parent.parent
GIT_USER_NAME = "John Doe"
GIT_USER_EMAIL = "john.doe@local.dev"
ANSWERS_FILE = ".copier-answers.yml"
DEFAULTS = dict(
    project_name="Test Project",
    project_description="A test project",
    author_fullname=GIT_USER_NAME,
    author_email=GIT_USER_EMAIL,
    author_username="john-doe",
    copyright_license="MIT License",
)

COLS = get_terminal_width()
LEFT_MARGIN = 10
GUTTER = 2
MARGINS = LEFT_MARGIN + GUTTER + 1
DIFF_WIDTH = COLS - MARGINS


@pytest.fixture(scope="session")
def copier_defaults() -> dict[str, Any]:
    return dict(
        project_name="Test Project",
        project_description="A test project",
        author_fullname=GIT_USER_NAME,
        author_email=GIT_USER_EMAIL,
        author_username="john-doe",
        copyright_license="MIT License",
    )


@pytest.fixture(scope="session")
def copier_template_paths() -> Sequence[str]:
    return (
        "template",
        "extensions",
        "copier.yml",
    )


# def run(cmd: str, *args, **kwargs) -> None:
#     args = [cmd, *args] if args else shlex.split(cmd)
#     return subprocess.run(args, **kwargs)


# @pytest.fixture(scope="session")
# def source(tmp_path_factory: pytest.TempPathFactory, gitconfig: GitConfig) -> Path:
#     src = tmp_path_factory.mktemp("src", False)

#     copytree(ROOT / "template", src / "template", dirs_exist_ok=True)
#     copytree(ROOT / "extensions", src / "extensions", dirs_exist_ok=True)
#     copy(ROOT / "copier.yml", src / "copier.yml")

#     run("git", "init", cwd=src)
#     run("git", "add", "-A", ".", cwd=src)
#     run("git", "commit", "-m", "test", cwd=src)
#     run("git", "tag", "99.99.99", cwd=src)

#     return src


# # @dataclass
# # class DirEqual:
# #     expected: Path
# #     actual: Path
# #     exclude: list[str]

# #     def __bool__(self):


# @dataclass
# class CopierHelper:
#     src: Path
#     dst: Path

#     def copy(self, **data):
#         run_copy(
#             str(self.src),
#             self.dst,
#             overwrite=True,
#             cleanup_on_error=False,
#             unsafe=True,
#             defaults=True,
#             data={**DEFAULTS, **data},
#         )
#         return Project(self.dst)


#     def update(self, **data) -> Project:
#         run_update(
#             str(self.src),
#             self.dst,
#             overwrite=True,
#             cleanup_on_error=False,
#             unsafe=True,
#             defaults=True,
#             data={**self.defaults, **data},
#         )
#         return Project(self.dst)

#     def load_answers(self, root: Path) -> dict[str, Any]:
#         file = root / ANSWERS_FILE
#         return {
#             key: value
#             for key, value in yaml.safe_load(file.read_text()).items()
#             if not key.startswith("_")
#         }

#     def assert_answers(self, expected: Path):
#         __tracebackhide__ = True
#         expected_answers = self.load_answers(expected)
#         answers = self.load_answers(self.dst)
#         assert answers == expected_answers

#     def assert_dst_equal(self, expected: Path):
#         __tracebackhide__ = True
#         assert_dir_equal(self.dst, expected, ignore=DEFAULT_IGNORES + [ANSWERS_FILE, "*cache*"])

#     def assert_pdm_scripts(self, *scripts: str):
#         # with local.cwd(self.dst):
#         for script in scripts:
#             run("pdm", script, cwd=self.dst)


# @dataclass
# class Project:
#     path: Path

#     def update(self, ):
#         pass

#     def assert_answers(self, expected: Path):
#         __tracebackhide__ = True
#         # expected_
#     #     expected = self.

#     # def load(self, path: Path):
#     #     data = super().load(path)
#     #     if path.name == ANSWERS_FILE:
#     #         # Only compare answers not metadata
#     #         data = {k: v for k, v in data.items() if not k.startswith("_")}
#     #     return data

#     def assert_equal(self, expected: Path):
#         __tracebackhide__ = True

#         assert self.dst == expected

#     def run(self, command: str, **kwargs):
#         run(*shlex.split(command), cwd=self.path, **kwargs)


# @pytest.fixture
# def copier(tmp_path: Path, source: Path) -> CopierHelper:
#     return CopierHelper(src=source, dst=tmp_path / "dst")
