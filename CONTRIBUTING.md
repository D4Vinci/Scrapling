# Contributing to Scrapling
Everybody is invited and welcome to contribute to Scrapling. Smaller changes have a better chance to get included in a timely manner. Adding unit tests for new features or test cases for bugs you've fixed help us to ensure that the Pull Request (PR) is fine.

There is a lot to do...
- If you are not a developer perhaps you would like to help with the [documentation](/docs)?
- If you are a developer, most of the features I'm planning to add in the future are moved to [roadmap file](/ROADMAP.md) so consider reading it.

Scrapling includes a comprehensive test suite which can be executed with pytest:
```bash
$ pytest
=============================== test session starts ===============================
platform darwin -- Python 3.12.7, pytest-8.3.3, pluggy-1.5.0
rootdir: /<some_where>/Scrapling
configfile: pytest.ini
plugins: cov-5.0.0, anyio-4.6.0
collected 16 items

tests/test_all_functions.py ................          [100%]

=============================== 16 passed in 0.22s ================================
```
Also, consider setting `debug` to `True` while initializing the Adaptor object so it's easier to know what's happening in the background.

### The process is straight-forward.

 - Read [How to get faster PR reviews](https://github.com/kubernetes/community/blob/master/contributors/guide/pull-requests.md#best-practices-for-faster-reviews) by Kubernetes (but skip step 0 and 1)
 - Fork Scrapling [git repository](https://github.com/D4Vinci/Scrapling).
 - Make your changes.
 - Ensure tests work.
 - Create a Pull Request against the [**dev**](https://github.com/D4Vinci/Scraplin/tree/dev) branch of Scrapling.