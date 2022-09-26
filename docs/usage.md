# Usage

```{eval-rst}
.. click:: loglicense.__main__:main
    :prog: loglicense
    :nested: full
```

## Report licenses

```console
$ loglicense report path_to/poetry.lock
```

Example output of this project's poetry.lock file:

```
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

The tool utilises [tabulate], giving it --tablefmt command can control
the format of the print. The table report can be saved using --output-file
to specify file. This makes it easy to integrate it in documentation
saving the default tablefmt (pipe) to .md file.

## Check licenses

```console
$ loglicense check path_to/poetry.lock --config-file path_to/.loglicense
```

This will using this projects .loglicense config file produce the following
and in this example exit with code 2 (due to coverage not achieved).

```
Found 9 dependencies
| Name               | License                            | Status   |
|:-------------------|:-----------------------------------|:---------|
| click              | BSD-3-Clause                       | Allowed  |
| colorama           | BSD                                | Allowed  |
| importlib-metadata | Apache Software License            | Unknown  |
| pathlib            | MIT License                        | Allowed  |
| tabulate           | MIT                                | Allowed  |
| toml               | MIT                                | Allowed  |
| typer              | MIT License                        | Allowed  |
| typing-extensions  | Python Software Foundation License | Unknown  |
| zipp               | MIT License                        | Allowed  |
Target license coverage (100%) and actual coverage: 77%
```

## Config file format

The config has three parameters you can use:

- **allow**: Explicitly list the licenses which you allow in your project
- **ban**: Explicitly list the license which you ban from your project
- **coverage**: The percentage of licenses which should be identfied and evaluated in your project. This is useful to catch unknown new licenses.

#### Example of a config file (looks for .loglicense by default)

```
[loglicense]
allow =
    MIT,
    BSD-3-Clause,
    BSD
ban =
    AGPL,
coverage = 100
```

[tabulate]: https://github.com/astanin/python-tabulate
