"""LogLicence main module."""
import json
import logging
from pathlib import Path
from typing import Any
from typing import List
from typing import Optional
from urllib.request import urlopen

from loglicense.utils import DependencyFileParser


logger = logging.getLogger("licenselogger")


class LicenseLogger:
    """Main module for logging licenses.

    Args:
        dependency_file: File to crawl dependencies for
        package_manager: Which type of package manager to evaluate.
            Defaults to pypi for python.
        info_columns: Information to include in table to log
        develop: Whether to include development dependencies

    """

    def __init__(
        self,
        dependency_file: str,
        package_manager: str = "pypi",
        info_columns: Optional[List[str]] = None,
        develop: bool = False,
    ):
        super().__init__()
        self.dependency_file = Path(dependency_file)
        self.package_manager = package_manager
        self.info_columns = info_columns if info_columns else ["name", "license"]
        self._parser_args = {"develop": develop}

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
    ) -> List[List[str]]:
        """Fetches license package metadata for the given dependency file.

        Returns:
            List[List[str]]: Metadata from licenses found in dependency
            file.
        """
        self.licenselog_ = [[x.capitalize() for x in self.info_columns]]

        for libname in self.parser(self.dependency_file, **self._parser_args):
            pkg_metadata = self.get_license_metadata(libname)
            lib_metadata = []
            if not pkg_metadata:
                lib_metadata.append(libname)
                lib_metadata.extend(
                    ["Not found" for x in range(len(self.info_columns) - 1)]
                )
            else:
                for col in self.info_columns:
                    licenses = pkg_metadata.get(col, "")

                    if not licenses:
                        licenses = ""
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

            self.licenselog_.append(lib_metadata)

        return self.licenselog_

    def get_license_metadata(self, libname: str) -> Any:
        """Fetch information from package manager site.

        Args:
            libname: Name of the package to fetch information regarding

        Returns:
            Any: The metadata of the library
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
        """Check if logged.

        Returns:
            bool: Whether logged or not
        """
        logged = [v for v in dir(self) if v.endswith("_") and not v.startswith("__")]

        return bool(len(logged))
