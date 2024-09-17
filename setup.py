from setuptools import setup

setup(
    name="ghlink",
    version="0.1.0",
    py_modules=["ghlink"],
    install_requires=[
        "gitpython",
        "requests",
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
    ],
    python_requires=">=3.6",
)
