# GitHub Link Generator Usage Guide

The GitHub Link Generator (`ghlink`) is a command-line tool that generates GitHub links for files in your Git repository. It supports both relative and absolute paths, and can generate links to specific lines or line ranges.

## Installation

You can install the GitHub Link Generator using pip:

```bash
pip install git+https://github.com/albertoperdomo2/ghlink.git
```

## Configuration

### Quick Setup

The easiest way to set up `ghlink` is to use the init command:

```bash
# Basic setup
ghlink init

# Setup with your GitHub token
ghlink init --token YOUR_GITHUB_TOKEN

# Setup with custom options
ghlink init --remote upstream --open-browser
```

### GitHub Token

`ghlink` works best with a GitHub personal access token for API authentication. This helps avoid rate limiting issues. You can provide your token in several ways:

1. During initialization:
   ```bash
   ghlink init --token YOUR_GITHUB_TOKEN
   ```

2. As an environment variable:
   ```bash
   export GITHUB_TOKEN=your_github_token_here
   ```

3. In the configuration file (`~/.config/ghlink/config`):
   ```
   [github]
   token = your_github_token_here
   default_remote = origin
   open_browser = false
   ```

To generate a token: Go to GitHub → Settings → Developer settings → Personal access tokens. Classic tokens with "repo" scope work fine.

## Basic Usage

After installation, you can use the `ghlink` command as follows:

1. Generate a link to a file:
   ```bash
   ghlink path/to/your/file.py
   ```

2. Generate a link to a specific line in a file:
   ```bash
   ghlink path/to/your/file.py -l 42
   ```

3. Generate a link to a range of lines in a file:
   ```bash
   ghlink path/to/your/file.py -l 42,50
   ```

## Advanced Options

### Remote Selection

Specify which Git remote to use (useful for forks with multiple remotes):

```bash
# Use a specific remote
ghlink path/to/your/file.py -r upstream

# Set a default remote
ghlink init --remote upstream
```

### Permalinks

Create permanent links that use commit SHA instead of branch name:

```bash
ghlink path/to/your/file.py -p
```

This ensures the link continues to point to the same version of the file, even if the branch changes.

### Browser Integration

Open links in your default web browser:

```bash
# Open this specific link
ghlink path/to/your/file.py -o

# Set browser opening as default behavior
ghlink init --open-browser
```

## Command Structure

`ghlink` has two main commands:

1. `init` - Initialize configuration:
   ```bash
   ghlink init [--token TOKEN] [--remote REMOTE] [--open-browser] [--config-path PATH]
   ```

2. `link` - Generate GitHub links (default command):
   ```bash
   ghlink link FILE_PATH [-l LINES] [-r REMOTE] [-p] [-o]
   ```

You can also use the simpler format without specifying the `link` command:
```bash
ghlink FILE_PATH [-l LINES] [-r REMOTE] [-p] [-o]
```

## Notes

- The tool works with both relative and absolute paths.
- Make sure you're in a Git repository when using the tool.
- The file must be pushed to the remote repository for the link to work.
- `ghlink` validates that line numbers exist in the file.
- The tool supports both HTTPS and SSH GitHub remote URLs.
- When in detached HEAD state, permalinks are automatically used.

## Examples

1. Using a relative path:
   ```bash
   ghlink ../lib/utils.py -l 10
   ```

2. Using an absolute path:
   ```bash
   ghlink /home/user/projects/myrepo/main.py -l 15,20
   ```

3. Creating a permalink to the current version:
   ```bash
   ghlink app.js -p
   ```

4. Using a different remote:
   ```bash
   ghlink models.py -r upstream
   ```

5. Opening the link in browser:
   ```bash
   ghlink README.md -o
   ```

6. Linking to the current file:
   ```bash
   ghlink $(basename $0)
   ```

For more information, run `ghlink --help`.
