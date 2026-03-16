"""Setup script for Feed to Somewhere."""

from pathlib import Path
from typing import List

from setuptools import find_packages, setup


PROJECT_ROOT = Path(__file__).resolve().parent


def read_requirements(filename: str) -> List[str]:
    """Read a pip requirements file and ignore comments and blank lines."""
    requirements_path = PROJECT_ROOT / filename
    return [
        line.strip()
        for line in requirements_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="feed-to-somewhere",
    version="0.1.0",
    description="A Python application that reads RSS feeds and saves them to a Notion database",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=read_requirements("requirements.txt"),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "feed-to-somewhere=feed_to_somewhere.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
