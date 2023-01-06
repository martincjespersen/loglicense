"""Utility functions for loglicense module."""
import re
from pathlib import Path
from typing import List
from typing import Set

import pkg_resources  # type: ignore
import toml


class DependencyFileParser:
    """Main module for DependencyFileParser."""

    def __init__(self) -> None:
        super().__init__()
        self.method_prefix = "parse_"
        self.parsers = {
            self.__get_dependency_filename(attribute): getattr(self, attribute)
            for attribute in dir(self)
            if callable(getattr(self, attribute))
            and attribute.startswith("parse") is True
        }

    def __get_dependency_filename(self, attribute: str) -> str:
        """Format the parser function name into original filename.

        Args:
            attribute: Name of the parser function

        Returns:
            str: Filename of the dependency file
        """
        dependency_filename = attribute.replace(self.method_prefix, "").replace(
            "_", "."
        )
        return dependency_filename

    @staticmethod
    def parse_poetry_lock(license_path: Path, develop: bool = False) -> List[str]:
        """Parser for poetry.lock files.

        Args:
            license_path: Path to license file (poetry.lock)
            develop: Whether to include development dependencies

        Returns:
            List[str]: List of the names of python depedencies in poetry file
        """
        output: List[str] = []
        included_categories: Set[str] = {"main"}

        if develop:
            included_categories.add("dev")

        license_file = toml.load(license_path)
        for pkg in license_file.get("package", []):
            if pkg["category"] in included_categories:
                version = pkg.get("version", "")
                output.append(pkg.get("name", "") + f"/{version}")
        return output

    @staticmethod
    def parse_requirements_txt(license_path: Path, develop: bool = False) -> List[str]:
        """Parser for requirements.txt files.

        Args:
            license_path: Path to license file (requirements.txt)
            develop: Whether to include development dependencies (requirements_dev.txt)

        Returns:
            List[str]: List of the names of python depedencies in requirements file
        """
        output: List[str] = []

        with license_path.open() as requirements_txt:
            output = [
                re.split(r"(\=\=|(>|<)+=?)", str(requirement))[0]  # ignore version
                for requirement in pkg_resources.parse_requirements(requirements_txt)
            ]

        if develop:
            dev_license_path = Path(str(license_path.absolute())[:-4] + "_dev.txt")
            if dev_license_path.is_file():
                with dev_license_path.open() as requirements_txt:
                    output.extend(
                        [
                            str(requirement).split("==")[0]  # ignore version
                            for requirement in pkg_resources.parse_requirements(
                                requirements_txt
                            )
                        ]
                    )

        return output

    @staticmethod
    def parse_pyproject_toml(license_path: Path, develop: bool = False) -> List[str]:
        """Parser for pyproject.toml files.

        Args:
            license_path: Path to license file (pyproject.toml)
            develop: Whether to include development dependencies

        Returns:
            List[str]: List of the names of python depedencies in pyproject file
        """
        output: List[str] = []
        license_file = toml.load(license_path)

        if "poetry" in license_file.get("tool", {}):
            dependencies = license_file["tool"]["poetry"].get("dependencies", {})
            dev_dependencies = license_file["tool"]["poetry"].get(
                "dev-dependencies", {}
            )
            if develop:
                dependencies.update(dev_dependencies)

            output = [x for x in dependencies.keys() if x != "python"]
        else:
            dependencies = license_file["project"].get("dependencies", {})
            dev_dependencies = license_file["project"].get("optional-dependencies", {})
            if dev_dependencies and isinstance(
                dev_dependencies[list(dev_dependencies.keys())[0]], list
            ):
                dev_dependencies = [
                    pkg
                    for test_type in dev_dependencies.keys()
                    for pkg in dev_dependencies[test_type]
                ]

            if develop:
                dependencies.extend(dev_dependencies)

            output = [
                x.project_name for x in pkg_resources.parse_requirements(dependencies)
            ]

        return output
