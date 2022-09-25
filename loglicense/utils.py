from pathlib import Path
from typing import List

import toml


class DependencyFileParser:
    """Main module for DependencyFileParser"""

    def __init__(self):
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
            dependency_filename: Filename of the dependency file
        """

        dependency_filename = attribute.replace(self.method_prefix, "").replace(
            "_", "."
        )
        return dependency_filename

    @staticmethod
    def parse_poetry_lock(license_file: Path) -> List[str]:
        """Main module for DependencyFileParser

        Args:
            license_file: Path to license file (poetry.lock)

        Returns:
            output: List of the names of python depedencies in lock file
        """
        output = []
        cf = toml.load(license_file)
        output = [pkg["name"] for pkg in cf.get("package", []) if "name" in pkg]
        return output
