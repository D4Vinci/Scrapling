from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="scrapling",
    version="0.1",
    description="""Scrapling is a powerful, flexible, and high-performance web scraping library for Python. It 
    simplifies the process of extracting data from websites, even when they undergo structural changes, and offers 
    impressive speed improvements over many popular scraping tools.""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Karim Shoair",
    author_email="karim.shoair@pm.me",
    license="BSD",
    packages=["scrapling",],
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
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Typing :: Typed",
    ],
    # Instead of using requirements file to dodge possible errors from tox?
    install_requires=[
        "requests>=2.3",
        "lxml>=4.5",
        "cssselect>=1.0",
        "w3lib",
        "orjson>=3",
        "tldextract",
    ],
    python_requires=">=3.6",
    url="https://github.com/D4Vinci/Scrapling",
    project_urls={
        "Documentation": "https://github.com/D4Vinci/Scrapling/Docs",  # For now
        "Source": "https://github.com/D4Vinci/Scrapling",
        "Tracker": "https://github.com/D4Vinci/Scrapling/issues",
    }
)
