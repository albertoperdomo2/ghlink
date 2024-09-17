# GitHub Link Generator Usage Guide

The GitHub Link Generator (`ghlink`) is a command-line tool that generates GitHub links for files in your Git repository. It supports both relative and absolute paths, and can generate links to specific lines or line ranges.

## Installation

You can install the GitHub Link Generator using pip:

```
pip install git+https://github.com/albertoperdomo2/ghlink.git
```

`ghlink` requires a GitHub personal access token for API authentication. This helps avoid rate limiting issues. Set up your token as follows:

1. Generate a personal access token on GitHub (Settings -> Developer settings -> Personal access tokens). Classic tokens with repo rights work fine.
2. Set the token as an environment variable:

```
export GITHUB_TOKEN=your_github_token_here
```

For permanent setup, add this line to your shell configuration file (e.g., .bashrc, .zshrc).

## Basic Usage

After installation, you can use the `ghlink` command as follows:

1. Generate a link to a file:
   ```
   ghlink path/to/your/file.py
   ```

2. Generate a link to a specific line in a file:
   ```
   ghlink path/to/your/file.py -l 42
   ```

3. Generate a link to a range of lines in a file:
   ```
   ghlink path/to/your/file.py -l 42,50
   ```

## Notes

- The tool works with both relative and absolute paths.
- Make sure you're in a Git repository when using the tool.
- The file must be pushed to the remote repository for the link to work.

## Examples

1. Using a relative path:
   ```
   ghlink ../lib/utils.py -l 10
   ```

2. Using an absolute path:
   ```
   ghlink /home/user/projects/myrepo/main.py -l 15,20
   ```

3. Linking to the current file:
   ```
   ghlink $(basename $0)
   ```

For more information, run `ghlink --help`.
