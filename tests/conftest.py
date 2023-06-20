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
from typing import Any, Iterator
# from plumbum import local
# from subprocess import run
import yaml
import subprocess

import icdiff
from copier.main import run_copy

import pytest

from pytest_gitconfig.plugin import GitConfig

from _pytest._code.code import TerminalRepr
from _pytest._io import TerminalWriter, get_terminal_width


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


def run(cmd: str, *args, **kwargs) -> None:
    args = [cmd, *args] if args else shlex.split(cmd)
    return subprocess.run(args, **kwargs)


# @dataclass
class ICDiffRepr(TerminalRepr):
    # name: str
    # expected: Path
    # actual: Path

    def actual_lines(self) -> list[str]:
        raise NotImplementedError()
    
    def expected_lines(self) -> list[str]:
        raise NotImplementedError()

    def toterminal(self, tw: TerminalWriter) -> None:
        differ = icdiff.ConsoleDiff(
            tabsize=2,
            cols=DIFF_WIDTH,
            highlight=True,
            truncate=True,
            line_numbers=True,
        )
        if not tw.hasmarkup:
            # colorization is disabled in Pytest - either due to the terminal not
            # supporting it or the user disabling it. We should obey, but there is
            # no option in icdiff to disable it, so we replace its colorization
            # function with a no-op
            differ.colorize = lambda string: string
            color_off = ""
        else:
            color_off = icdiff.color_codes["none"]
        
        lines = differ.make_table(
            self.expected_lines(),
            self.actual_lines(),
            "Expected",
            "Actual",
            context=True
        )
        for line in lines:
            tw.line(color_off + line)


@dataclass
class ReprDiffError(TerminalRepr):
    name: str
    expected: Path
    actual: Path

    def toterminal(self, tw: TerminalWriter) -> None:
        expected = (Path(self.expected) / self.name).read_text()
        actual = (Path(self.actual) / self.name).read_text()
        differ = icdiff.ConsoleDiff(
            tabsize=2,
            cols=DIFF_WIDTH,
            highlight=True,
            truncate=True,
            line_numbers=True,
        )
        if not tw.hasmarkup:
            # colorization is disabled in Pytest - either due to the terminal not
            # supporting it or the user disabling it. We should obey, but there is
            # no option in icdiff to disable it, so we replace its colorization
            # function with a no-op
            differ.colorize = lambda string: string
            color_off = ""
        else:
            color_off = icdiff.color_codes["none"]
        
        lines = differ.make_table(
            expected.splitlines(),
            actual.splitlines(),
            # "Expected",
            # "Actual",
            context=True
        )
        for line in lines:
            tw.line(color_off + line)


@dataclass
class AnsersDiffRepr(ICDiffRepr):
    expected: dict
    actual: dict

    def _as_lines(self, answers: dict) -> list[str]:
        return [
            f"{key}={yaml.safe_bump(value)}"
            for key, value in answers.items()
            if not key.startswith("_")
        ]

    def actual_lines(self) -> list[str]:
        return self._as_lines(self.actual)
    
    def expected_lines(self) -> list[str]:
        return self._as_lines(self.expected)

    # def toterminal(self, tw: TerminalWriter) -> None:
    #     expected = (Path(self.expected) / self.name).read_text()
    #     actual = (Path(self.actual) / self.name).read_text()
    #     differ = icdiff.ConsoleDiff(
    #         tabsize=2,
    #         cols=tw.fullwidth - MARGINS,
    #         highlight=True,
    #         truncate=True,
    #         line_numbers=True,
    #     )
    #     if not tw.hasmarkup:
    #         # colorization is disabled in Pytest - either due to the terminal not
    #         # supporting it or the user disabling it. We should obey, but there is
    #         # no option in icdiff to disable it, so we replace its colorization
    #         # function with a no-op
    #         differ.colorize = lambda string: string
    #         color_off = ""
    #     else:
    #         color_off = icdiff.color_codes["none"]
        
    #     lines = differ.make_table(
    #         expected.splitlines(),
    #         actual.splitlines(),
    #         "Expected",
    #         "Actual",
    #         context=True
    #     )
    #     for line in lines:
    #         tw.line(color_off + line)


def report_recursive(dcmp, tw: TerminalWriter, prefix: Path | None = None):
    prefix = prefix or Path("")
    line_length = tw.fullwidth - LEFT_MARGIN
    for name in dcmp.diff_files:
        tw.line(f"{prefix / name} differs, see the diff below")
        diff_header = f"[ {prefix / name} diff ]"
        half_header = int((line_length - len(diff_header)) / 2)
        tw.line(half_header * "-" + diff_header + half_header * "-")
        ReprDiffError(name, expected=dcmp.right, actual=dcmp.left).toterminal(tw)
        diff_footer = f"[ end of {prefix / name} diff ]"
        half_footer = int((line_length - len(diff_footer)) / 2)
        tw.line(half_footer * "-" + diff_footer + half_footer * "-")
    for name in dcmp.left_only:
        tw.line(f"{prefix / name} file is not expected in result")
    for name in dcmp.right_only:
        tw.line(f"{prefix / name} is missing from result")
    for name, sub_dcmp in dcmp.subdirs.items():
        prefix = Path(name) if not prefix else (prefix / name)
        report_recursive(sub_dcmp, tw, prefix=prefix)


def pytest_assertrepr_compare(config: pytest.Config, op: str, left: Any, right: Any):
    if op != "==":
        return
    if isinstance(left, Path) and left.is_dir() and isinstance(right, Path) and right.is_dir():
        actual = left
        expected = right
        diff = filecmp.dircmp(actual, expected, ignore=filecmp.DEFAULT_IGNORES + [ANSWERS_FILE, "*cache*"])
        tw = TerminalWriter(out := StringIO())
        tw.hasmarkup = True
        tw.line("Some files are different")
        report_recursive(diff, tw)
        return out.getvalue().splitlines()


@pytest.fixture(scope="session")
def source(tmp_path_factory: pytest.TempPathFactory, gitconfig: GitConfig) -> Path:
    src = tmp_path_factory.mktemp("src", False)

    copytree(ROOT / "template", src / "template", dirs_exist_ok=True)
    copytree(ROOT / "extensions", src / "extensions", dirs_exist_ok=True)
    copy(ROOT / "copier.yml", src / "copier.yml")

    run("git", "init", cwd=src)
    run("git", "add", "-A", ".", cwd=src)
    run("git", "commit", "-m", "test", cwd=src)
    run("git", "tag", "99.99.99", cwd=src)

    return src



@dataclass
class CopierHelper:
    src: Path
    dst: Path

    def copy(self, **data):
        run_copy(
            str(self.src),
            self.dst,
            overwrite=True,
            cleanup_on_error=False,
            unsafe=True,
            defaults=True,
            data={**DEFAULTS, **data},
        )
        return Project(self.dst)

    def update(
        self,
    ):
        pass

    def load_answers(self, root: Path) -> dict[str, Any]:
        file = root / ANSWERS_FILE
        return {
            key: value
            for key, value in yaml.safe_load(file.read_text()).items()
            if not key.startswith("_")
        }

    def assert_answers(self, expected: Path):
        __tracebackhide__ = True
        expected_answers = self.load_answers(expected)
        answers = self.load_answers(self.dst)
        assert answers == expected_answers

    def assert_dst_equal(self, expected: Path):
        __tracebackhide__ = True
        
        assert self.dst == expected

    def assert_pdm_scripts(self, *scripts: str):
        # with local.cwd(self.dst):
        for script in scripts:
            run("pdm", script, cwd=self.dst)


@dataclass
class Project:
    path: Path

    def update(self, ):
        pass
    
    def assert_answers(self, expected: Path):
        __tracebackhide__ = True
        # expected_
    #     expected = self.
        
    # def load(self, path: Path):
    #     data = super().load(path)
    #     if path.name == ANSWERS_FILE:
    #         # Only compare answers not metadata
    #         data = {k: v for k, v in data.items() if not k.startswith("_")}
    #     return data

    def assert_equal(self, expected: Path):
        __tracebackhide__ = True
        
        assert self.dst == expected

    def run(self, command: str, **kwargs):
        run(*shlex.split(command), cwd=self.path, **kwargs)


@pytest.fixture
def copier(tmp_path: Path, source: Path) -> CopierHelper:
    return CopierHelper(src=source, dst=tmp_path / "dst")
