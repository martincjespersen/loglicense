"""Test cases for the __main__ module."""
from pathlib import Path
from typing import List

import pytest

from loglicense import DependencyFileParser
from loglicense import LicenseLogger


@pytest.mark.parametrize(
    "filename",
    ("poetry.lock",),
)
@pytest.mark.parametrize(
    "content",
    (
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
        """,
    ),
)
@pytest.mark.parametrize(
    "packages",
    (["alabaster", "atomicwrites"],),
)
def test_dependency_file_parser(filename, content, packages, tmp_path) -> None:
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

    assert list(parser.keys())[0] == filename
    assert parser[filename](tmp_path, develop=True) == packages
    assert parser[filename](tmp_path, develop=False) == []


@pytest.mark.parametrize(
    "filename",
    ("poetry.lock",),
)
@pytest.mark.parametrize(
    "content",
    (
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
        """,
    ),
)
@pytest.mark.parametrize(
    "result",
    ([["name", "license"], ["alabaster", "BSD License"], ["atomicwrites", "MIT"]],),
)
def test_license_logger_pypi(
    filename: str, content: str, result: List[str], tmp_path: Path
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
        dependency_file=tmp_path,
        package_manager="pypi",
        info_columns=["name", "license"],
        develop=True,
    )
    assert not license_log.is_logged()
    licenses = license_log.log_licenses()
    assert license_log.is_logged()
    assert licenses == result
