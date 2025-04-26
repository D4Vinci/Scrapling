import os
import subprocess
import sys
from pathlib import Path

import click

from scrapling.core.shell import CustomShell


def get_package_dir():
    return Path(os.path.dirname(__file__))


def run_command(command, line):
    print(f"Installing {line}...")
    _ = subprocess.check_call(command, shell=False)  # nosec B603
    # I meant to not use try except here


@click.command(help="Install all Scrapling's Fetchers dependencies")
@click.option(
    "-f",
    "--force",
    "force",
    is_flag=True,
    default=False,
    type=bool,
    help="Force Scrapling to reinstall all Fetchers dependencies",
)
def install(force):
    if (
        force
        or not get_package_dir().joinpath(".scrapling_dependencies_installed").exists()
    ):
        run_command(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            "Playwright browsers",
        )
        run_command(
            [sys.executable, "-m", "playwright", "install-deps", "chromium", "firefox"],
            "Playwright dependencies",
        )
        run_command(
            [sys.executable, "-m", "camoufox", "fetch", "--browserforge"],
            "Camoufox browser and databases",
        )
        # if no errors raised by above commands, then we add below file
        get_package_dir().joinpath(".scrapling_dependencies_installed").touch()
    else:
        print("The dependencies are already installed")


@click.command(help="Interactive scraping console")
@click.option(
    "-c",
    "--code",
    "code",
    is_flag=False,
    default="",
    type=str,
    help="Evaluate the code in the shell, print the result and exit",
)
@click.option(
    "-L",
    "--loglevel",
    "level",
    is_flag=False,
    default="debug",
    type=click.Choice(
        ["debug", "info", "warning", "error", "critical", "fatal"], case_sensitive=False
    ),
    help="Log level (default: DEBUG)",
)
def shell(code, level):
    console = CustomShell(code=code, log_level=level)
    console.start()


@click.group()
def main():
    pass


# Adding commands
main.add_command(install)
main.add_command(shell)
