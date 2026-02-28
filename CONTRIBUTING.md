# Contributing to Scrapling

Thank you for your interest in contributing to Scrapling! 

Everybody is invited and welcome to contribute to Scrapling. 

Minor changes are more likely to be included promptly. Adding unit tests for new features or test cases for bugs you've fixed helps us ensure that the Pull Request (PR) is acceptable.

There are many ways to contribute to Scrapling. Here are some of them:

- Report bugs and request features using the [GitHub issues](https://github.com/D4Vinci/Scrapling/issues). Please follow the issue template to help us resolve your issue quickly.
- Blog about Scrapling. Tell the world how you’re using Scrapling. This will help newcomers with more examples and increase the Scrapling project's visibility.
- Join the [Discord community](https://discord.gg/EMgGbDceNQ) and share your ideas on how to improve Scrapling. We’re always open to suggestions.
- If you are not a developer, perhaps you would like to help with translating the [documentation](https://github.com/D4Vinci/Scrapling/tree/docs)?

## Making a Pull Request
To ensure that your PR gets accepted, please make sure that your PR is based on the latest changes from the dev branch and that it satisfies the following requirements:

- **The PR must be made against the [**dev**](https://github.com/D4Vinci/Scrapling/tree/dev) branch of Scrapling. Any PR made against the main branch will be rejected.**
- **The code should be passing all available tests. We use tox with GitHub's CI to run the current tests on all supported Python versions for every code-related commit.**
- **The code should be passing all code quality checks like `mypy` and `pyright`. We are using GitHub's CI to enforce code style checks as well.**
- **Make your changes, keep the code clean with an explanation of any part that might be vague, and remember to create a separate virtual environment for this project.**
- If you are adding a new feature, please add tests for it.
- If you are fixing a bug, please add code with the PR that reproduces the bug.
- Please follow the rules and coding style rules we explain below.


## Finding work

If you have decided to make a contribution to Scrapling, but you do not know what to contribute, here are some ways to find pending work:

- Check out the [contribution](https://github.com/D4Vinci/Scrapling/contribute) GitHub page, which lists open issues tagged as `good first issue`. These issues provide a good starting point.
- There are also the [help wanted](https://github.com/D4Vinci/Scrapling/issues?q=is%3Aissue%20label%3A%22help%20wanted%22%20state%3Aopen) issues, but know that some may require familiarity with the Scrapling code base first. You can also target any other issue, provided it is not tagged as `invalid`, `wontfix`, or similar tags.
- If you enjoy writing automated tests, you can work on increasing our test coverage. Currently, the test coverage is around 90–92%.
- Join the [Discord community](https://discord.gg/EMgGbDceNQ) and ask questions in the `#help` channel.

## Coding style
Please follow these coding conventions as we do when writing code for Scrapling:
- We use [pre-commit](https://pre-commit.com/) to automatically address simple code issues before every commit, so please install it and run `pre-commit install` to set it up. This will install hooks to run [ruff](https://docs.astral.sh/ruff/), [bandit](https://github.com/PyCQA/bandit), and [vermin](https://github.com/netromdk/vermin) on every commit. We are currently using a workflow to automatically run these tools on every PR, so if your code doesn't pass these checks, the PR will be rejected.
- We use type hints for better code clarity and [pyright](https://github.com/microsoft/pyright)/[mypy](https://github.com/python/mypy) for static type checking. If your code isn't acceptable by those tools, your PR won't pass the code quality rule.
- We use the conventional commit messages format as [here](https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13#types), so for example, we use the following prefixes for commit messages:
   
   | Prefix      | When to use it           |
   |-------------|--------------------------|
   | `feat:`     | New feature added        |
   | `fix:`      | Bug fix                  |
   | `docs:`     | Documentation change/add |
   | `test:`     | Tests                    |
   | `refactor:` | Code refactoring         |
   | `chore:`    | Maintenance tasks        |
    
    Then include the details of the change in the commit message body/description.

   Example:
   ```
   feat: add `adaptive` for similar elements
   
   - Added find_similar() method
   - Implemented pattern matching
   - Added tests and documentation
   ```

> Please don’t put your name in the code you contribute; git provides enough metadata to identify the author of the code.

## Development

### Getting started

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/<your-username>/Scrapling.git
   cd Scrapling
   git checkout dev
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[all]"
   pip install -r tests/requirements.txt
   ```

3. Install browser dependencies:
   ```bash
   scrapling install
   ```

4. Set up pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Tips

Setting the scrapling logging level to `debug` makes it easier to know what's happening in the background.
```python
import logging
logging.getLogger("scrapling").setLevel(logging.DEBUG)
```
Bonus: You can install the beta of the upcoming update from the dev branch as follows
```commandline
pip3 install git+https://github.com/D4Vinci/Scrapling.git@dev
```

## Tests
Scrapling includes a comprehensive test suite that can be executed with pytest. However, first, you need to install all libraries and `pytest-plugins` listed in `tests/requirements.txt`. Then, running the tests will result in an output like this:
   ```bash
   $ pytest tests -n auto
   =============================== test session starts ===============================
   platform darwin -- Python 3.13.8, pytest-8.4.2, pluggy-1.6.0 -- /Users/<redacted>/.venv/bin/python3.13
   cachedir: .pytest_cache
   rootdir: /Users/<redacted>/scrapling
   configfile: pytest.ini
   plugins: asyncio-1.2.0, anyio-4.11.0, xdist-3.8.0, httpbin-2.1.0, cov-7.0.0
   asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
   10 workers [515 items]
   scheduling tests via LoadScheduling

   ...<shortened>...

   =============================== 271 passed in 52.68s ==============================
   ```
Here, `-n auto` runs tests in parallel across multiple processes to increase speed.

**Note:** You may need to run browser tests sequentially (`DynamicFetcher`/`StealthyFetcher`) to avoid conflicts. To run non-browser tests in parallel and browser tests separately:
```bash
# Non-browser tests (parallel)
pytest tests/ -k "not (DynamicFetcher or StealthyFetcher)" -n auto

# Browser tests (sequential)
pytest tests/ -k "DynamicFetcher or StealthyFetcher"
```

Bonus: You can also see the test coverage with the `pytest` plugin below
```bash
pytest --cov=scrapling tests/
```

## Building Documentation
Documentation is built using [Zensical](https://zensical.org/). You can build it locally using the following commands:
```bash
pip install zensical
pip install -r docs/requirements.txt
zensical build --clean  # Build the static site
zensical serve          # Local preview
```
