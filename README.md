# GitHub Link Generator

GitHub Link Generator (`ghlink`) is a command-line tool that generates GitHub links for files in your Git repository. It supports both relative and absolute paths, and can generate links to specific lines or line ranges.

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

## How It Works

1. `ghlink` first checks if the specified file exists in your local repository.
2. It then verifies if the file is pushed to the remote GitHub repository.
3. If the file exists and is pushed, it generates the appropriate GitHub link.
4. For line-specific links, it adds the line numbers to the URL.

## Documentation

For more detailed usage instructions, please see the [usage guide](docs/usage.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
