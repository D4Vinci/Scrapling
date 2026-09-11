# Command Line Interface

Since v0.3, Scrapling includes a powerful command-line interface that provides three main capabilities:

1. **Interactive Shell**: An interactive Web Scraping shell based on IPython that provides many shortcuts and useful tools
2. **Extract Commands**: Scrape websites from the terminal without any programming
3. **Utility Commands**: Installation and management tools

```bash
# Launch interactive shell
scrapling shell

# Convert the content of a page to markdown and save it to a file
scrapling extract get "https://example.com" content.md

# Get help for any command
scrapling --help
scrapling extract --help
```

## Requirements
This section requires you to install the extra `shell` dependency group, like the following:
```bash
pip install "scrapling[shell]"
```
and the installation of the fetchers' dependencies with the following command
```bash
scrapling install
```
This downloads all browsers, along with their system dependencies and fingerprint manipulation dependencies.

!!! note "Non-Debian Linux distributions (Arch Linux, Fedora, Alpine, etc.)"
    On Linux systems where `apt-get` is unavailable, `scrapling install` downloads the Chromium browser and completes the setup, but skips automatic system package installation. If Chromium fails to launch, install any missing system libraries using your distribution's package manager.