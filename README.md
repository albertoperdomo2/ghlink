# GitHub Link Generator

GitHub Link Generator (`ghlink`) is a command-line tool that generates GitHub links for files in your Git repository. It supports both relative and absolute paths, and can generate links to specific lines or line ranges.

## Installation

You can install the GitHub Link Generator using pip:

```bash
pip install git+https://github.com/albertoperdomo2/ghlink.git
```

## Configuration

You can quickly set up `ghlink` with the new `init` command:

```bash
# Basic setup
ghlink init

# Setup with your GitHub token
ghlink init --token YOUR_GITHUB_TOKEN
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

## Advanced Features

### Permalinks

Create permanent links using commit SHA instead of branch name:

```bash
ghlink path/to/your/file.py -p
```

### Remote Selection

Specify which Git remote to use (useful for forks):

```bash
ghlink path/to/your/file.py -r upstream
```

### Browser Integration

Open links directly in your browser:

```bash
ghlink path/to/your/file.py -o
```

## How It Works

1. `ghlink` first checks if the specified file exists in your local repository.
2. It verifies that the file is pushed to the remote GitHub repository.
3. For line-specific links, it validates that the specified lines exist in the file.
4. It handles both HTTPS and SSH GitHub URLs to work with any repository setup.
5. When in detached HEAD state, it automatically uses the current commit SHA.
6. If the file exists and is pushed, it generates the appropriate GitHub link and copies it to your clipboard.
7. Based on your configuration, it can automatically open the link in your browser.

## Documentation

For more detailed usage instructions, please see the [usage guide](docs/usage.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
