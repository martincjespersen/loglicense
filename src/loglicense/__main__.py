"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Log License."""


if __name__ == "__main__":
    main(prog_name="loglicense")  # pragma: no cover
