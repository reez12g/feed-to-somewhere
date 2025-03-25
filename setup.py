"""Setup script for Feed to Somewhere."""

from setuptools import setup, find_packages

setup(
    name="feed-to-somewhere",
    version="0.1.0",
    description="A Python application that reads RSS feeds and saves them to a Notion database",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "beautifulsoup4>=4.12.0",
        "feedparser>=6.0.0",
        "notion-client>=2.0.0",
        "requests>=2.25.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "feed-to-somewhere=feed_to_somewhere.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
