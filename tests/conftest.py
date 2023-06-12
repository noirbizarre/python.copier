
from dataclasses import dataclass
import os
from pathlib import Path
from shutil import copytree, ignore_patterns
from sys import stderr, stdout
from plumbum import local
from plumbum.cmd import git

import pytest
from dir_content_diff import get_comparators, YamlComparator, compare_trees

ROOT = Path(__file__).parent.parent
GIT_USER_NAME = "John Doe"
GIT_USER_EMAIL = "john.doe@local.dev"

copier = local["copier"]
pdm = local["pdm"]

ANSWERS_FILE = ".copier-answers.yml"


class AnswersComparator(YamlComparator):
    def load(self, path: Path):
        data = super().load(path)
        if path.name == ANSWERS_FILE:
            # Only compare answers not metadata
            data = {k: v for k, v in data.items() if not k.startswith("_")}
        return data


comparators = get_comparators()
comparators[".yml"] = AnswersComparator()


@dataclass
class TplHelper:
    src: Path
    dst: Path
    gitconfig: Path

    def copy(
        self, 
        project_name: str = "Test Project",
        project_description: str = "A test project",
        author_fullname: str = GIT_USER_NAME,
        author_email: str = GIT_USER_EMAIL,
        author_username: str = "john-doe",
        copyright_license: str = "MIT License",
        **data
    ):
        args = []
        for key, value in data.items():
            args.append("-d")
            args.append(f"{key}={value}")
        cmd = (copier["copy", "--UNSAFE", "-f", self.src, self.dst, "--defaults",
            "-d", f"project_name={project_name}",
            "-d", f"project_description={project_description}",
            "-d", f"author_fullname={author_fullname}",
            "-d", f"author_email={author_email}",
            "-d", f"author_username={author_username}",
            "-d", f"copyright_license={copyright_license}",
            *args
        ] > stdout) >= stdout
        cmd()

    def update(self, ):
        pass

    def assert_dst_equal(self, expected: Path):
        __tracebackhide__ = True

        if diff := compare_trees(expected, self.dst, comparators=comparators):
            from pprint import pprint
            pprint(diff)
            sep = "\n - "
            raise AssertionError(
                "\n\n".join(["Some files are differents"] + [
                    f"{path}:\n - {sep.join(error.splitlines()[1:])}"
                    for path, error in sorted(diff.items(), key=lambda x: x[0])
                ])
            )
    
    def assert_pdm_scripts(self, *scripts: str):
        with local.cwd(self.dst):
            for script in scripts:
                cmd = (pdm[script] > stdout) >= stdout
                cmd()



@pytest.fixture
def tpl(tmp_path: Path) -> TplHelper:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    gitconfig = tmp_path / "gitconfig"

            
    # Clear any GIT_ prefixed environment variable
    for var in os.environ:
        if var.startswith("GIT_") and var in local.env:
            # monkeypatch.delenv(var)
            del local.env[var]
    
    local.env["GIT_CONFIG_GLOBAL"] = str(gitconfig)

    # Define a dedicated temporary git config
    if not gitconfig.parent.exists():
        gitconfig.parent.mkdir()

    git("config", "--file", str(gitconfig), "user.name", GIT_USER_NAME)
    git("config", "--file", str(gitconfig), "user.email", GIT_USER_EMAIL)
    git("config", "--file", str(gitconfig), "init.defaultBranch", "main")

    ignored = ignore_patterns(".git", ".venv", ".pytest_cache")
    # ignored = ignore_patterns("^.*")
    copytree(ROOT, src, dirs_exist_ok=True, ignore=ignored)

    with local.cwd(src):
        git("init")
        git("add", "-A", ".")
        git("commit", "-m", "test")
        git("tag", "99.99.99")

    return TplHelper(src=src, dst=dst, gitconfig=gitconfig)


