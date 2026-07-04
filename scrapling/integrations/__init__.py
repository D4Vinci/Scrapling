"""Integrations with third-party frameworks.

Each integration lives in its own module and is imported explicitly, so its
framework never becomes a required dependency of Scrapling. Example::

    from scrapling.integrations.scrapy import scrapling_response
"""
