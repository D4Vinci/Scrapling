from pathlib import Path

from setuptools import find_packages, setup

long_description = Path("README.md").read_text(encoding="utf-8")


setup(
    name="scrapling",
    version="0.2.99",
    description="""Scrapling is an undetectable, powerful, flexible, high-performance Python library that makes Web Scraping easy again! In an internet filled with complications,
    it simplifies web scraping, even when websites' design changes, while providing impressive speed that surpasses almost all alternatives.""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Karim Shoair",
    author_email="karim.shoair@pm.me",
    license="BSD",
    packages=find_packages(),
    zip_safe=False,
    package_dir={
        "scrapling": "scrapling",
    },
    entry_points={
        "console_scripts": ["scrapling=scrapling.cli:main"],
    },
    include_package_data=True,
    classifiers=[
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        # "Development Status :: 6 - Mature",
        # "Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Text Processing :: Markup",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Typing :: Typed",
    ],
    # Instead of using requirements file to dodge possible errors from tox?
    install_requires=[
        "lxml>=5.0",
        "cssselect>=1.2",
        "IPython",
        "click",
        "w3lib",
        "orjson>=3",
        "tldextract",
        "httpx[brotli,zstd, socks]",
        "playwright>=1.49.1",
        "rebrowser-playwright>=1.49.1",
        "camoufox[geoip]>=0.4.11",
    ],
    python_requires=">=3.9",
    url="https://github.com/D4Vinci/Scrapling",
    project_urls={
        "Documentation": "https://scrapling.readthedocs.io/en/latest/",
        "Source": "https://github.com/D4Vinci/Scrapling",
        "Tracker": "https://github.com/D4Vinci/Scrapling/issues",
    },
)
