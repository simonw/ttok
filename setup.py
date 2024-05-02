from setuptools import setup
import os

VERSION = "0.3"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="ttok",
    description="Count and truncate text based on tokens",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/ttok",
    project_urls={
        "Issues": "https://github.com/simonw/ttok/issues",
        "CI": "https://github.com/simonw/ttok/actions",
        "Changelog": "https://github.com/simonw/ttok/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["ttok"],
    entry_points="""
        [console_scripts]
        ttok=ttok.cli:cli
    """,
    install_requires=["click", "tiktoken"],
    extras_require={"test": ["pytest", "cogapp"]},
    python_requires=">=3.8",
)
