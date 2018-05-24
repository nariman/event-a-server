"""
Event Bot Server
"""

from setuptools import setup


def content(filename, splitlines=False):
    with open(filename) as f:
        return f.read().splitlines() if splitlines else f.read()


long_description = content("README.md")
requirements = content("requirements.txt", splitlines=True)

setup(
    name="eventbot",
    description="Event Bot Server",
    long_description=long_description,
    version="2017.12.0",

    author="Nariman Safiulin",
    author_email="",

    license="",

    packages=["eventbot"],

    install_requires=requirements,

    classifiers=(
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Natural Language :: Russian",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
    ),
)
