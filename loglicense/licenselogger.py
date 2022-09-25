"""Main module."""
import json
import logging
from pathlib import Path
from typing import Any
from typing import List
from urllib.request import urlopen

from loglicense import DependencyFileParser


logger = logging.getLogger("licenselogger")


class LicenseLogger:
    """Main module for logging licenses.

    Args:
        dependency_file: File to crawl dependencies for
        package_manager: Which type of package manager to evaluate.
            Defaults to pypi for python.
        info_columns: Information to include in table to log

    """

    def __init__(
        self,
        dependency_file: str,
        package_manager: str = "pypi",
        info_columns: Optional[List[str]] = None,
    ):
        super().__init__()
        self.dependency_file = Path(dependency_file)
        self.package_manager = package_manager
        self.info_columns = info_columns if info_columns else ["name", "license"]

        if not self.dependency_file.is_file():
            raise ValueError("Path must be a file")

        self.parser = DependencyFileParser().parsers[self.dependency_file.name]

        if self.package_manager == "pypi":
            self.library_url = "https://pypi.python.org/pypi/XXX/json"
        # elif self.package_manager == "npm":
        #     self.library_url = "https://registry.npmjs.org/XXX/latest"
        else:
            raise NotImplementedError("Only supports pypi dependencies")

    def log_licenses(
        self,
    ):
        """Fetches license information from package manger for the
        given dependency file
        """

        self.licenselog_ = [self.info_columns]

        for libname in self.parser(self.dependency_file):
            pkg_metadata = self.get_license_metadata(libname)
            lib_metadata = []

            for col in self.info_columns:
                if pkg_metadata:

                    licenses = pkg_metadata.get(col, "")
                    if col == "license" and licenses.strip() == "":
                        classifiers = pkg_metadata.get("classifiers", "")
                        licenses = [
                            classifier.replace("License :: ", "").replace(
                                "OSI Approved :: ", ""
                            )
                            for classifier in classifiers
                            if classifier.startswith("License")
                        ]
                        licenses = "\n".join(licenses)

                    lib_metadata.append(licenses)
                else:
                    lib_metadata.append("Not found")

            self.licenselog_.append(lib_metadata)

        return self.licenselog_

    def get_license_metadata(self, libname: str) -> Any:
        """Fetch information from package manager site

        Args:
            libname: Name of the package to fetch information regarding
        Returns:
            output: The metadata of the library
        """
        lib_url = self.library_url.replace("XXX", libname)
        try:
            with urlopen(lib_url) as libfile:
                output = json.loads(libfile.read().decode())

                if self.package_manager == "pypi":
                    output = output.get("info", {})

            return output

        except Exception:
            logger.warning(f"{libname}: error in fetching metadata")
            return None

    def is_logged(self) -> bool:
        logged = [
            v for v in getattr(self) if v.endswith("_") and not v.startswith("__")
        ]

        return bool(len(logged))
