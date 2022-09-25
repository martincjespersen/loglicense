"""Command-line interface."""
import configparser
from difflib import get_close_matches
from pathlib import Path
from typing import List
from typing import Optional

import typer
from tabulate import tabulate

from loglicense import LicenseLogger


app = typer.Typer()


@app.command()
def report(
    dependency_file: str,
    package_manager: str = "pypi",
    info_columns: List[str] = ["name", "license"],
    tablefmt: str = "pipe",
    output_file: Optional[str] = None,
):

    license_log = LicenseLogger(
        dependency_file=dependency_file,
        package_manager=package_manager,
        info_columns=info_columns,
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


OK, ERR, FAIL_UNDER = 0, 1, 2


@app.command()
def check(
    dependency_file: str,
    config_file: str = ".loglicense",
    package_manager: str = "pypi",
    show_report: bool = True,
) -> int:

    config = configparser.ConfigParser()
    config.read(config_file)
    config = config["loglicense"]

    license_log = LicenseLogger(
        dependency_file=dependency_file,
        package_manager=package_manager,
        info_columns=["name", "license"],
    )

    allowed = {
        x.lower().strip() for x in config.get("allow", "").split(",") if x.strip()
    }
    banned = {x.lower().strip() for x in config.get("ban", "").split(",") if x.strip()}

    results = [["Name", "License", "Status"]]
    for lib in license_log.log_licenses()[1:]:

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

    if show_report:
        pretty_print = tabulate(results, tablefmt="pipe", headers="firstrow")
        print(pretty_print)

    result_status = [x for x in results[1:][-1]]

    if any([x == "Banned" for x in result_status]):
        return ERR

    license_coverage = int(
        (result_status.count("Allowed") / len(result_status[1:])) * 100
    )
    if "coverage" in config:
        target_cov = int(config.get("coverage"))
        print(
            f"Target license coverage ({target_cov}%) and actual coverage: {license_coverage}%"
        )
        if license_coverage < target_cov:
            return ERR

    return OK


if __name__ == "__main__":
    app()
