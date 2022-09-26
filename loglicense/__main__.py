"""Command-line interface."""
import configparser
from difflib import get_close_matches
from pathlib import Path
from typing import List
from typing import Optional
from typing import Set

import typer
from tabulate import tabulate

from loglicense import LicenseLogger


app = typer.Typer()
OK, ERR, FAIL_UNDER = 0, 1, 2


@app.command()
def report(
    dependency_file: str,
    package_manager: str = "pypi",
    info_columns: Optional[List[str]] = None,
    tablefmt: str = "pipe",
    develop: bool = False,
    output_file: Optional[str] = None,
):
    """Document licenses of packages in dependency file.

    Args:
        dependency_file: File to crawl dependencies for
        package_manager: Which type of package manager to evaluate.
            Defaults to pypi for python.
        info_columns: Information to include in table to log
        tablefmt: Tabulates formatting argument
        develop: Whether to include development dependencies
        output_file: File to save table of licenses in
    """
    info_columns = info_columns if info_columns else ["name", "license"]

    license_log = LicenseLogger(
        dependency_file=dependency_file,
        package_manager=package_manager,
        info_columns=info_columns,
        develop=develop,
    )
    license_table = tabulate(
        license_log.log_licenses(), tablefmt=tablefmt, headers="firstrow"
    )

    if output_file:
        output_filepath = Path(output_file)
        output_filepath.touch(exist_ok=True)
        output_filepath.write_text(license_table)
    else:
        print(license_table)


@app.command()
def check(
    dependency_file: str,
    config_file: str = ".loglicense",
    package_manager: str = "pypi",
    develop: bool = False,
    show_report: bool = True,
) -> int:
    """Check licenses of packages in dependency file.

    Args:
        dependency_file: File to crawl dependencies for
        config_file: Config for parameters of the license check
        package_manager: Which type of package manager to evaluate.
            Defaults to pypi for python.
        develop: Whether to include development dependencies
        show_report: Print information regarding licences checked

    Returns:
        int: finish code
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    config = config["loglicense"]

    license_log = LicenseLogger(
        dependency_file=dependency_file,
        package_manager=package_manager,
        info_columns=["name", "license"],
        develop=develop,
    )

    allowed = {
        x.lower().strip() for x in config.get("allow", "").split(",") if x.strip()
    }
    banned = {x.lower().strip() for x in config.get("ban", "").split(",") if x.strip()}
    results = validate_requirements(license_log, allowed, banned)

    if show_report:
        print(f"Found {len(results)-1} dependencies")
        pretty_print = tabulate(results, tablefmt="pipe", headers="firstrow")
        print(pretty_print)

    result_status = [x[-1] for x in results[1:]]

    if any([x == "Banned" for x in result_status]):
        return ERR

    try:
        license_coverage = int(
            (result_status.count("Allowed") / len(result_status)) * 100
        )
    except ZeroDivisionError:
        license_coverage = 100

    if "coverage" in config:
        target_cov = int(config.get("coverage"))
        print(
            f"Target license coverage ({target_cov}%) "
            f"and actual coverage: {license_coverage}%"
        )
        if license_coverage < target_cov:
            return ERR

    return OK


def validate_requirements(
    license_logger: LicenseLogger, allowed: Set[str], banned: Set[str]
) -> List[List[str]]:
    """Compare licenses to requirements.

    Args:
        license_logger: File to crawl dependencies for
        allowed: Whether to include development dependencies
        banned: Print information regarding licences checked

    Returns:
        List[List[str]]: Returns results of validation of license
    """
    results = [["Name", "License", "Status"]]
    for lib in license_logger.log_licenses()[1:]:

        # handle multiple licenses
        for lib_license in lib[-1].split("\n"):
            matches = None
            if banned:
                matches = get_close_matches(
                    lib_license.lower().replace("license", ""), banned
                )
                if matches:
                    results.append([lib[0], lib_license, "Banned"])
                    continue

            if allowed:
                matches = get_close_matches(
                    lib_license.lower().replace("license", ""), allowed
                )
                if matches:
                    results.append([lib[0], lib_license, "Allowed"])

                if not matches:
                    results.append([lib[0], lib_license, "Unknown"])

            else:
                if not matches:
                    results.append([lib[0], lib_license, "Allowed"])

    return results


if __name__ == "__main__":
    app()
