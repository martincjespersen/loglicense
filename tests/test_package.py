"""Test cases for the __main__ module."""
from pathlib import Path
from typing import List

import pytest

from loglicense import DependencyFileParser
from loglicense import LicenseLogger


@pytest.mark.parametrize(
    "filename, content, packages",
    [
        (
            "poetry.lock",
            """[[package]]
name = "alabaster"
version = "0.7.12"
description = "A configurable sidebar-enabled Sphinx theme"
category = "dev"
optional = false
python-versions = "*"

[[package]]
name = "atomicwrites"
version = "1.4.0"
description = "Atomic file writes."
category = "dev"
optional = false
python-versions = ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*"
""",
            ["alabaster/0.7.12", "atomicwrites/1.4.0"],
        ),
        (
            "requirements.txt",
            """alabaster==0.7.12
atomicwrites>=1.4.0
        """,
            ["alabaster", "atomicwrites"],
        ),
        (
            "pyproject.toml",
            """[tool.poetry.dependencies]
python = "^3.7"

[tool.poetry.dev-dependencies]
alabaster = "0.7.12"
atomicwrites = "^1.4.0"

""",
            ["alabaster", "atomicwrites"],
        ),
        (
            "pyproject.toml",
            """[project]
dependencies = []

[project.optional-dependencies]
test = [
    "alabaster==0.20.4",
    "atomicwrites >=1.6.2,!=1.7,!=1.7.1,!=1.7.2,!=1.7.3,!=1.8,!=1.8.1,<2.0.0",
]
""",
            ["alabaster", "atomicwrites"],
        ),
    ],
)
def test_dependency_file_parser(
    filename: str, content: str, packages: List[str], tmp_path: Path
) -> None:
    """Test of dependency file parser.

    Args:
        filename: Filename to build and test
        content: Content of file to test
        packages: Expected packages to find
        tmp_path: Path to temporary directory
    """
    tmp_path = tmp_path / filename
    tmp_path.touch(exist_ok=False)
    tmp_path.write_text(content)

    parser = DependencyFileParser().parsers

    assert filename in parser
    assert parser[filename](tmp_path, develop=True) == packages
    if filename != "requirements.txt":
        assert parser[filename](tmp_path, develop=False) == []


@pytest.mark.parametrize(
    "filename, content, result",
    [
        (
            "poetry.lock",
            """
            [[package]]
            name = "alabaster"
            version = "0.7.12"
            description = "A configurable sidebar-enabled Sphinx theme"
            category = "dev"
            optional = false
            python-versions = "*"

            [[package]]
            name = "atomicwrites"
            version = "1.4.0"
            description = "Atomic file writes."
            category = "dev"
            optional = false
            python-versions = ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*"

            [[package]]
            name = "SOMETGINF"
            version = "1.4.0"
            description = "Atomic file writes."
            category = "dev"
            """,
            [
                ["Name", "License"],
                ["alabaster", "BSD License"],
                ["atomicwrites", "MIT"],
                ["SOMETGINF", "Not found"],
            ],
        )
    ],
)
def test_license_logger_pypi(
    filename: str, content: str, result: List[List[str]], tmp_path: Path
) -> None:
    """Test of license logger for pypi package manager.

    Args:
        filename: Filename to build and test
        content: Content of file to test
        result: Expected result of test
        tmp_path: Path to temporary directory
    """
    tmp_path = tmp_path / filename
    tmp_path.touch(exist_ok=False)
    tmp_path.write_text(content)

    license_log = LicenseLogger(
        dependency_file=str(tmp_path),
        package_manager="pypi",
        info_columns=["name", "license"],
        develop=True,
    )
    assert not license_log.is_logged()
    licenses = license_log.log_licenses()
    assert license_log.is_logged()
    assert licenses == result


@pytest.mark.parametrize(
    "filename",
    ("poetry.lock", ""),
)
def test_license_logger_file_err(filename: str, tmp_path: Path) -> None:
    """Test of license logger error handling.

    Args:
        filename: Filename to build and test
        tmp_path: Path to temporary directory
    """
    tmp_path = tmp_path / filename
    if filename:
        tmp_path.touch(exist_ok=False)

    try:
        license_log = LicenseLogger(
            dependency_file=str(tmp_path),
            package_manager="pypi",
            info_columns=["name", "license"],
            develop=True,
        )
        license_log.log_licenses()
        assert filename == "poetry.lock"
    except ValueError:
        assert filename == ""


@pytest.mark.parametrize(
    "pkg_manager",
    ("pypi", "npm"),
)
def test_license_logger_file_not_implemented(pkg_manager: str, tmp_path: Path) -> None:
    """Test of license logger not implemented handling.

    Args:
        pkg_manager: Which package manager to run
        tmp_path: Path to temporary directory
    """
    tmp_path = tmp_path / "poetry.lock"
    tmp_path.touch(exist_ok=False)
    try:
        license_log = LicenseLogger(
            dependency_file=str(tmp_path),
            package_manager=pkg_manager,
            info_columns=["name", "license"],
            develop=True,
        )
        license_log.log_licenses()
        assert pkg_manager == "pypi"
    except NotImplementedError:
        assert pkg_manager == "npm"
