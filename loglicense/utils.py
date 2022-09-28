"""Utility functions for loglicense module."""
from pathlib import Path
from typing import List
from typing import Set

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
        """Main module for DependencyFileParser.

        Args:
            license_path: Path to license file (poetry.lock)
            develop: Whether to include development dependencies

        Returns:
            List[str]: List of the names of python depedencies in lock file
        """
        output: List[str] = []
        included_categories: Set[str] = {"main"}

        if develop:
            included_categories.add("dev")

        license_file = toml.load(license_path)
        for pkg in license_file.get("package", []):
            if pkg["category"] in included_categories:
                output.append(pkg.get("name", ""))
        return output
