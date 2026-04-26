"""Utility functions for loglicense module."""
import fnmatch
from collections import deque
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Set

import toml
from packaging.requirements import Requirement


class DependencyFileParser:
    """Main module for DependencyFileParser."""

    _FUZZY_PATTERNS = (
        ("uv*.lock", "uv.lock"),
        ("poetry*.lock", "poetry.lock"),
    )

    def __init__(self) -> None:
        super().__init__()
        self.method_prefix = "parse_"
        self.parsers = {
            self.__get_dependency_filename(attribute): getattr(self, attribute)
            for attribute in dir(self)
            if callable(getattr(self, attribute))
            and attribute.startswith("parse") is True
        }

    def resolve(self, filename: str) -> Optional[Callable[..., List[str]]]:
        """Look up a parser for the given filename.

        Tries exact match against the registered parser keys first, then a
        small set of glob-style fallbacks so non-canonical names like
        ``uv-test.lock`` route to the uv parser.

        Args:
            filename: Basename of the dependency file.

        Returns:
            Optional[Callable]: The parser callable, or ``None`` if no match.
        """
        if filename in self.parsers:
            return self.parsers[filename]
        for pattern, target in self._FUZZY_PATTERNS:
            if fnmatch.fnmatch(filename, pattern) and target in self.parsers:
                return self.parsers[target]
        return None

    @staticmethod
    def _parse_requirements(lines: Iterable[str]) -> Iterator[Requirement]:
        """Yield ``Requirement`` objects from PEP 508 lines.

        Mirrors ``pkg_resources.parse_requirements``: strips comments and
        whitespace, skips empty lines and pip directives (``-r``, ``-e`` ...).

        Args:
            lines: Iterable of raw requirement lines (e.g. an open file).

        Yields:
            Requirement: Parsed requirement objects.
        """
        for raw in lines:
            line = raw.split("#", 1)[0].strip()
            if not line or line.startswith("-"):
                continue
            yield Requirement(line)

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
            if (
                not pkg.get("category")
                or pkg.get("category", "") in included_categories
            ):
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
                req.name
                for req in DependencyFileParser._parse_requirements(requirements_txt)
            ]

        if develop:
            dev_license_path = Path(str(license_path.absolute())[:-4] + "_dev.txt")
            if dev_license_path.is_file():
                with dev_license_path.open() as requirements_txt:
                    output.extend(
                        req.name
                        for req in DependencyFileParser._parse_requirements(
                            requirements_txt
                        )
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
                req.name
                for req in DependencyFileParser._parse_requirements(dependencies)
            ]

        return output

    @staticmethod
    def parse_uv_lock(license_path: Path, develop: bool = False) -> List[str]:
        """Parser for uv.lock files.

        Identifies the editable/virtual project root (the entry whose source
        is `editable` or `virtual`), reads its `dependencies` and
        `[package.dev-dependencies]` to determine direct main vs dev roots,
        then walks the resolved package list to filter out dev-only packages
        when ``develop=False``.

        Markers on dep edges are ignored (treated as always-reachable, matching
        the "include all resolved" stance of poetry.lock parsing). Extras
        (`extra = [...]`) on dep edges are not walked into the depended
        package's `[package.optional-dependencies]` table.

        Args:
            license_path: Path to license file (uv.lock)
            develop: Whether to include development dependencies

        Returns:
            List[str]: List of the names of python dependencies in uv.lock file
        """
        license_file = toml.load(license_path)
        packages: List[Dict[str, Any]] = license_file.get("package", []) or []

        root: Optional[Dict[str, Any]] = None
        for pkg in packages:
            source = pkg.get("source") or {}
            if isinstance(source, dict) and ("editable" in source or "virtual" in source):
                root = pkg
                break

        def _emit(pkg: Dict[str, Any]) -> str:
            name = pkg.get("name", "")
            version = pkg.get("version", "")
            return f"{name}/{version}" if version else name

        if root is None:
            return [_emit(pkg) for pkg in packages if pkg.get("name")]

        root_name = root.get("name", "")

        adjacency: Dict[str, Set[str]] = {}
        for pkg in packages:
            name = pkg.get("name")
            if not name:
                continue
            edges = adjacency.setdefault(name, set())
            for dep in pkg.get("dependencies", []) or []:
                dep_name = dep.get("name") if isinstance(dep, dict) else None
                if dep_name:
                    edges.add(dep_name)

        def _direct_names(deps: Any) -> Set[str]:
            result: Set[str] = set()
            for dep in deps or []:
                if isinstance(dep, dict) and dep.get("name"):
                    result.add(dep["name"])
            return result

        main_roots = _direct_names(root.get("dependencies"))

        dev_roots: Set[str] = set()
        for group_deps in (root.get("dev-dependencies") or {}).values():
            dev_roots |= _direct_names(group_deps)

        def _reachable(starts: Set[str]) -> Set[str]:
            seen: Set[str] = set()
            queue: deque = deque(starts)
            while queue:
                node = queue.popleft()
                if node in seen:
                    continue
                seen.add(node)
                for nxt in adjacency.get(node, ()):
                    if nxt not in seen:
                        queue.append(nxt)
            return seen

        if develop:
            keep = {pkg.get("name") for pkg in packages if pkg.get("name")} - {root_name}
        else:
            keep = _reachable(main_roots) - {root_name}

        return [_emit(pkg) for pkg in packages if pkg.get("name") in keep]
