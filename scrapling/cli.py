import os
import sys
import subprocess
from pathlib import Path

from click import command, option, Choice, group


def get_package_dir():
    return Path(os.path.dirname(__file__))


def run_command(cmd, line):
    print(f"Installing {line}...")
    _ = subprocess.check_call(cmd, shell=False)  # nosec B603
    # I meant to not use try except here


@command(help="Install all Scrapling's Fetchers dependencies")
@option(
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
        # if no errors raised by the above commands, then we add the below file
        get_package_dir().joinpath(".scrapling_dependencies_installed").touch()
    else:
        print("The dependencies are already installed")


@command(help="Interactive scraping console")
@option(
    "-c",
    "--code",
    "code",
    is_flag=False,
    default="",
    type=str,
    help="Evaluate the code in the shell, print the result and exit",
)
@option(
    "-L",
    "--loglevel",
    "level",
    is_flag=False,
    default="debug",
    type=Choice(
        ["debug", "info", "warning", "error", "critical", "fatal"], case_sensitive=False
    ),
    help="Log level (default: DEBUG)",
)
def shell(code, level):
    from scrapling.core.shell import CustomShell

    console = CustomShell(code=code, log_level=level)
    console.start()


@group()
def main():
    pass


# Adding commands
main.add_command(install)
main.add_command(shell)
