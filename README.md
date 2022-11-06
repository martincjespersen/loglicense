# Log License

[![PyPI](https://img.shields.io/pypi/v/loglicense.svg)][pypi_]
![Downloads](https://img.shields.io/pypi/dm/loglicense)
[![Status](https://img.shields.io/pypi/status/loglicense.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/loglicense)][python version]
[![License](https://img.shields.io/pypi/l/loglicense)][license]

[![Read the documentation at https://loglicense.readthedocs.io/](https://img.shields.io/readthedocs/loglicense/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/martincjespersen/loglicense/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/martincjespersen/loglicense/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/loglicense/
[status]: https://pypi.org/project/loglicense/
[python version]: https://pypi.org/project/loglicense
[read the docs]: https://loglicense.readthedocs.io/
[tests]: https://github.com/martincjespersen/loglicense/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/martincjespersen/loglicense
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features

- Report and save log of licenses included in project

### Supported dependency files

- poetry.lock

### Supported package managers

- pypi

## Installation

You can install _Log License_ via [pip] from [PyPI]:

```console
$ pip install loglicense
```

or using [Poetry]

```console
$ poetry add loglicense
```

## Quick example

Please see the [Command-line Reference] for details.

```console
$ loglicense report path_to/poetry.lock
```

Example output of this project's poetry.lock file:

```console
| name               | license                            |
|:-------------------|:-----------------------------------|
| click              | BSD-3-Clause                       |
| colorama           | BSD                                |
| importlib-metadata | Apache Software License            |
| pathlib            | MIT License                        |
| tabulate           | MIT                                |
| toml               | MIT                                |
| typer              | MIT License                        |
| typing-extensions  | Python Software Foundation License |
| zipp               | MIT License                        |
```

Alternatively you can let it search the executed directory for any supported file

```console
$ loglicense report
```

## Features to implement

- Support npmjs package manager (and package.json/package-lock.json)
- Support Pipfile, pyproject.toml, Pipfile.lock, requirements.txt

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [Apache 2.0 license][license],
_Log License_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/martincjespersen/loglicense/issues
[pip]: https://pip.pypa.io/

This project is greatly inspired by [dep-license] created by [Abdulelah Bin Mahfoodh].

[dep-license]: https://github.com/abduhbm/dep-license
[abdulelah bin mahfoodh]: https://github.com/abduhbm
[poetry]: https://python-poetry.org/

<!-- github-only -->

[license]: https://github.com/martincjespersen/loglicense/blob/main/LICENSE
[contributor guide]: https://github.com/martincjespersen/loglicense/blob/main/CONTRIBUTING.md
[command-line reference]: https://loglicense.readthedocs.io/en/latest/usage.html
