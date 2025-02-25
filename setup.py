from setuptools import setup
import re

# Get version from the ghlink.py file
with open("ghlink.py", "r") as f:
    version_match = re.search(r'^__version__ = ["\']([^"\']*)["\']', f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        version = "1.0.0"  # Default if not found

setup(
    name="ghlink",
    version=version,
    py_modules=["ghlink"],
    install_requires=[
        "gitpython",
        "requests",
        "pyperclip",  # Added missing dependency
    ],
    entry_points={
        "console_scripts": [
            "ghlink=ghlink:main",
        ],
    },
    author="Alberto Perdomo",
    author_email="hello@albertoperdomo.me",
    description="A tool to generate GitHub links (from the terminal) for files in a Git repository",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/albertoperdomo2/ghlink",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Utilities",
    ],
    keywords="github, git, link, permalink, terminal, cli",
    python_requires=">=3.6",
)
