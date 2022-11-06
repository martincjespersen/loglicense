"""Test cases for the __main__ module."""
from pathlib import Path

from typer.testing import CliRunner

from loglicense.__main__ import app


runner = CliRunner()


def test_app_report(tmp_path: Path) -> None:
    """Test of dependency file parser.

    Args:
        tmp_path: Path to temporary directory
    """
    tmp_path = tmp_path / "poetry.lock"
    tmp_path.touch(exist_ok=False)
    tmp_path.write_text(
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
        """
    )

    output = """| name         | license     |
|:-------------|:------------|
| alabaster    | BSD License |
| atomicwrites | MIT         |
| SOMETGINF    | Not found   |"""

    result = runner.invoke(
        app, ["report", "--dependency-file", str(tmp_path), "--develop"]
    )
    assert result.exit_code == 0
    assert output in result.stdout


def test_app_check_ok(tmp_path: Path) -> None:
    """Test of dependency file parser.

    Args:
        tmp_path: Path to temporary directory
    """
    tmp_conf = tmp_path / ".loglicense"
    tmp_conf.touch(exist_ok=False)
    tmp_conf.write_text(
        """
[loglicense]
ban =
     AGPL,
"""
    )

    tmp_file = tmp_path / "poetry.lock"
    tmp_file.touch(exist_ok=False)
    tmp_file.write_text(
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
        """
    )

    result = runner.invoke(
        app, ["check", str(tmp_file), "--config-file", str(tmp_conf), "--develop"]
    )
    assert result.exit_code == 0


def test_app_check_err(tmp_path: Path) -> None:
    """Test of dependency file parser.

    Args:
        tmp_path: Path to temporary directory
    """
    tmp_conf = tmp_path / ".loglicense"
    tmp_conf.touch(exist_ok=False)
    tmp_conf.write_text(
        """
[loglicense]
ban =
    MIT
coverage = 100
"""
    )

    tmp_file = tmp_path / "poetry.lock"
    tmp_file.touch(exist_ok=False)
    tmp_file.write_text(
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
        """
    )

    result = runner.invoke(
        app, ["check", str(tmp_file), "--config-file", str(tmp_conf), "--develop"]
    )
    assert result.exit_code == 1


def test_app_check_fail_under(tmp_path: Path) -> None:
    """Test of dependency file parser.

    Args:
        tmp_path: Path to temporary directory
    """
    tmp_conf = tmp_path / ".loglicense"
    tmp_conf.touch(exist_ok=False)
    tmp_conf.write_text(
        """
[loglicense]
allow =
    MIT,
    BSD-3-Clause,
    BSD
coverage = 100"""
    )

    tmp_file = tmp_path / "poetry.lock"
    tmp_file.touch(exist_ok=False)
    tmp_file.write_text(
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
        """
    )

    result = runner.invoke(
        app, ["check", str(tmp_file), "--config-file", str(tmp_conf), "--develop"]
    )
    assert result.exit_code == 2
