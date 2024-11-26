from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="scrapling",
    version="0.2.7",
    description="""Scrapling is a powerful, flexible, and high-performance web scraping library for Python. It 
    simplifies the process of extracting data from websites, even when they undergo structural changes, and offers 
    impressive speed improvements over many popular scraping tools.""",
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
    include_package_data=True,
    classifiers=[
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta ",
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
        "Programming Language :: Python :: 3.8",
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
        "requests>=2.3",
        "lxml>=4.5",
        "cssselect>=1.2",
        "w3lib",
        "orjson>=3",
        "tldextract",
        'httpx[brotli,zstd]',
        'playwright==1.48',  # Temporary because currently All libraries that provide CDP patches doesn't support playwright 1.49 yet
        'rebrowser-playwright',
        'camoufox>=0.3.10',
        'browserforge',
    ],
    python_requires=">=3.8",
    url="https://github.com/D4Vinci/Scrapling",
    project_urls={
        "Documentation": "https://github.com/D4Vinci/Scrapling/tree/main/docs",  # For now
        "Source": "https://github.com/D4Vinci/Scrapling",
        "Tracker": "https://github.com/D4Vinci/Scrapling/issues",
    }
)
