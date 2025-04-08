Thank you for your interest in contributing to Scrapling! 

Everybody is invited and welcome to contribute to Scrapling. 

Smaller changes have a better chance of getting included in a timely manner. Adding unit tests for new features or test cases for bugs you've fixed helps us to ensure that the Pull Request (PR) is acceptable.

There is a lot to do...

- If you are not a developer, you can help us improve the documentation.
- If you are a developer, most of the features I'm planning to add in the future are moved to [roadmap file](https://github.com/D4Vinci/Scrapling/blob/main/ROADMAP.md), so consider reading it.

## Running tests
Scrapling includes a comprehensive test suite that can be executed with pytest, but first, you need to install all libraries and `pytest-plugins` inside `tests/requirements.txt`. Then, running the tests will result in an output like this:
   ```bash
   $ pytest tests
   =============================== test session starts ===============================
   platform darwin -- Python 3.12.8, pytest-8.3.3, pluggy-1.5.0 -- /Users/<redacted>/.venv/bin/python3.12
   cachedir: .pytest_cache
   rootdir: /Users/<redacted>/scrapling
   configfile: pytest.ini
   plugins: cov-5.0.0, asyncio-0.25.0, base-url-2.1.0, httpbin-2.1.0, playwright-0.5.2, anyio-4.6.2.post1, xdist-3.6.1, typeguard-4.3.0
   asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=function
   collected 83 items 
   
   ...<shortened>...
   
   =============================== 83 passed in 157.52s (0:02:37) =====================
   ```
Hence, you can add `-n auto` to the command above to run tests in threads to increase speed.

Bonus: You can also see the test coverage with the pytest plugin below
```bash
pytest --cov=scrapling tests/
```

## Installing the latest unstable version from the dev branch
```bash
pip3 install git+https://github.com/D4Vinci/Scrapling.git@dev
```

## Development
Setting the scrapling logging level to `debug` makes it easier to know what's happening in the background.
   ```python
   >>> import logging
   >>> logging.getLogger("scrapling").setLevel(logging.DEBUG)
   ```
### Code Style

We use:

1. Type hints for better code clarity
2. Flake8, bandit, isort, and other hooks through `pre-commit`. <br/>Please install the hooks before committing with:
     ```bash
     pip install pre-commit
     pre-commit install
     ```
    It will run automatically on the code you push with each commit.
3. Conventional commit messages format. We use the below format for commit messages
   
   | Prefix      | When to use it           |
   |-------------|--------------------------|
   | `feat:`     | New feature added        |
   | `fix:`      | Bug fix                  |
   | `docs:`     | Documentation change/add |
   | `test:`     | Tests                    |
   | `refactor:` | Code refactoring         |
   | `chore:`    | Maintenance tasks        |

   Example:
   ```
   feat: add auto-matching for similar elements
   
   - Added find_similar() method
   - Implemented pattern matching
   - Added tests and documentation
   ```

### Push changes to the library

Then, the process is straightforward.

 - Read [How to get faster PR reviews](https://github.com/kubernetes/community/blob/master/contributors/guide/pull-requests.md#best-practices-for-faster-reviews) by Kubernetes (but skip step 0 and 1)
 - Fork Scrapling [Git repository](https://github.com/D4Vinci/Scrapling.git).
 - Make your changes, and don't forget to create a separate virtual environment for this project.
 - Ensure all tests are passing.
 - Create a Pull Request against the [**dev**](https://github.com/D4Vinci/Scrapling/tree/dev) branch of Scrapling.

A bonus: if you have more than one version of Python installed, you can use tox to run tests on each version with:
```bash
pip install tox
tox
```

> Note: All tests are automatically run with each push on Github on all supported Python versions using tox, so ensure all tests pass, or your PR will not be accepted.


## Building Documentation
```bash
pip install mkdocs-material
mkdocs serve  # Local preview
mkdocs build  # Build the static site
```