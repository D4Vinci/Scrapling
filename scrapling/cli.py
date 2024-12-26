import os
import subprocess
import sys
from pathlib import Path

import click


def get_package_dir():
    return Path(os.path.dirname(__file__))


def run_command(command, line):
    print(f"Installing {line}...")
    _ = subprocess.check_call(command, shell=True)
    # I meant to not use try except here


@click.command(help="Install all Scrapling's Fetchers dependencies")
def install():
    if not get_package_dir().joinpath(".scrapling_dependencies_installed").exists():
        run_command([sys.executable, "-m", "playwright", "install", 'chromium'], 'Playwright browsers')
        run_command([sys.executable, "-m", "playwright", "install-deps", 'chromium', 'firefox'], 'Playwright dependencies')
        run_command([sys.executable, "-m", "camoufox", "fetch", '--browserforge'], 'Camoufox browser and databases')
        # if no errors raised by above commands, then we add below file
        get_package_dir().joinpath(".scrapling_dependencies_installed").touch()
    else:
        print('The dependencies are already installed')


@click.group()
def main():
    pass


# Adding commands
main.add_command(install)
