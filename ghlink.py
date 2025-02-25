#!/usr/bin/env python3
"""
GitHub Link Generator - A CLI tool to generate GitHub links for files in a Git repository.

This tool allows you to quickly generate GitHub links for files in your local repository,
including support for line ranges and permalinks.
"""

import argparse
import os
import pyperclip
import requests
import sys
import webbrowser
import re
from configparser import ConfigParser
from pathlib import Path

from git import Repo, InvalidGitRepositoryError

__version__ = "1.0.0"


def get_repo_info(repo_path, remote_name='origin'):
    """Get repository information from the local git repo.
    
    Args:
        repo_path (str): Path to a file or directory in the git repository
        remote_name (str): Name of the git remote to use
        
    Returns:
        tuple: (owner, repo_name, branch, repo, remote)
    
    Raises:
        SystemExit: If not a git repository or remote not found
    """
    try:
        repo = Repo(repo_path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        print("Error: Not a git repository.")
        sys.exit(1)

    try:
        remote = repo.remote(name=remote_name)
        remote_url = remote.url
    except ValueError:
        print(f"Error: Remote '{remote_name}' not found.")
        print("Available remotes:")
        for r in repo.remotes:
            print(f"  - {r.name}")
        sys.exit(1)

    # extract owner and repo name from the remote URL
    # handle both HTTPS and SSH URLs
    if remote_url.startswith('http'):
        # HTTPS URLs: https://github.com/owner/repo.git
        match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', remote_url)
    else:
        # SSH URLs: git@github.com:owner/repo.git
        match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', remote_url)
    
    if not match:
        print(f"Error: Could not parse GitHub URL: {remote_url}")
        sys.exit(1)
        
    owner, repo_name = match.groups()
    
    try:
        branch = repo.active_branch.name
    except TypeError:
        print("Warning: You are in detached HEAD state. Using current commit as reference.")
        branch = repo.head.commit.hexsha[:7]
    
    return owner, repo_name, branch, repo, remote


def is_file_pushed(repo, remote, file_path, branch):
    """Check if the file has been pushed to the remote branch.
    
    Args:
        repo (git.Repo): Repository object
        remote (git.Remote): Remote object
        file_path (str): Relative path to the file
        branch (str): Branch name
        
    Returns:
        bool: True if file is pushed, False otherwise
    """
    try:
        # check if the branch exists on the remote
        if branch not in [ref.name.split('/')[-1] for ref in remote.refs]:
            print(f"Warning: Branch '{branch}' does not exist on remote '{remote.name}'.")
            return False

        remote_ref = f"{remote.name}/{branch}"
        
        # check if there are unpushed commits
        if hasattr(repo.heads, branch):
            local_commits = list(repo.iter_commits(f"{remote_ref}..{branch}"))
            
            if local_commits:
                print(f"Warning: You have {len(local_commits)} unpushed commits.")
                return False
        
        # check if the file exists in the remote branch
        remote_commit = repo.refs[remote_ref].commit
        try:
            # convert path separators to match git's internal format
            git_path = file_path.replace(os.path.sep, '/')
            remote_commit.tree[git_path]
            return True
        except KeyError:
            return False
    except Exception as e:
        print(f"Error checking if file is pushed: {e}")
        return False


def generate_link(owner, repo_name, ref, file_path, line_start, line_end=None):
    """Generate a GitHub link for the file and optional line numbers.
    
    Args:
        owner (str): Repository owner
        repo_name (str): Repository name
        ref (str): Branch, tag or commit SHA
        file_path (str): Path to the file within the repository
        line_start (int, optional): Starting line number
        line_end (int, optional): Ending line number
        
    Returns:
        str: GitHub URL for the file
    """
    base_url = f"https://github.com/{owner}/{repo_name}/blob/{ref}/{file_path}"

    if line_start and line_end:
        return f"{base_url}#L{line_start}-L{line_end}"
    elif line_start:
        return f"{base_url}#L{line_start}"
    else:
        return base_url


def get_config():
    """Get configuration from config file.
    
    Returns:
        dict: Configuration options
    """
    config = {
        'token': os.environ.get("GITHUB_TOKEN"),
        'default_remote': 'origin',
        'open_browser': False
    }
    
    # check for token in config file
    config_paths = [
        os.path.expanduser("~/.config/ghlink/config"),
        os.path.expanduser("~/.github_link_config")  # legacy location
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            conf = ConfigParser()
            conf.read(config_path)
            if 'github' in conf:
                if 'token' in conf['github'] and not config['token']:
                    config['token'] = conf['github']['token']
                if 'default_remote' in conf['github']:
                    config['default_remote'] = conf['github']['default_remote']
                if 'open_browser' in conf['github']:
                    config['open_browser'] = conf['github']['open_browser'].lower() in ('true', 'yes', '1')
            break
    
    return config


def get_github_token():
    """Get GitHub token from environment variable or config file.
    
    Returns:
        str: GitHub token or None
    """
    config = get_config()
    return config.get('token')


def check_file_exists_on_github(owner, repo_name, ref, file_path):
    """Check if a file exists on GitHub using the GitHub API.
    
    Args:
        owner (str): Repository owner
        repo_name (str): Repository name
        ref (str): Branch, tag or commit SHA
        file_path (str): Path to the file within the repository
        
    Returns:
        bool: True if file exists, False otherwise
    """
    token = get_github_token()
    headers = {"Authorization": f"token {token}"} if token else {}
    
    # URL encode the file path
    encoded_path = '/'.join(part for part in file_path.split('/'))
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{encoded_path}?ref={ref}"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
            print("GitHub API rate limit exceeded. Set GITHUB_TOKEN environment variable to increase limit.")
            return False
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error checking GitHub: {e}")
        return False


def count_file_lines(file_path):
    """Count the number of lines in a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        int: Number of lines or 0 on error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception as e:
        print(f"Error counting lines in file: {e}")
        return 0


def create_config_file(config_path, token=None, remote='origin', open_browser=False):
    """Create a configuration file template.
    
    Args:
        config_path (str): Path to the config file
        token (str, optional): GitHub token
        remote (str, optional): Default git remote to use
        open_browser (bool, optional): Whether to open links in browser by default
    """
    config = ConfigParser()
    config['github'] = {
        'token': token or 'your_github_token_here',
        'default_remote': remote,
        'open_browser': str(open_browser).lower()
    }
    
    os.makedirs(os.path.dirname(os.path.expanduser(config_path)), exist_ok=True)
    with open(os.path.expanduser(config_path), 'w') as f:
        config.write(f)
    
    print(f"Created config file at {config_path}")
    if not token:
        print("Edit this file to add your GitHub token and preferences.")


def cmd_init(args):
    """Handle the init subcommand to create configuration file.
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit code
    """
    config_path = os.path.expanduser(args.config_path or "~/.config/ghlink/config")
    create_config_file(config_path, args.token, args.remote, args.open_browser)
    print(f"Configuration initialized. Run 'ghlink --help' to see available commands.")
    
    if args.token:
        print("GitHub token has been saved.")
    else:
        print(f"TIP: Generate a token at https://github.com/settings/tokens")
        print(f"     Then run: ghlink init --token YOUR_TOKEN")
    
    return 0


def cmd_link(args):
    """Handle the default link generation command.
    
    Args:
        args: Command line arguments
        
    Returns:
        int: Exit code
    """
    # get the absolute path of the file
    file_path = os.path.abspath(args.file_path)

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return 1

    # get the repo root directory
    try:
        repo = Repo(file_path, search_parent_directories=True)
        repo_root = repo.git.rev_parse("--show-toplevel")
    except InvalidGitRepositoryError:
        print("Error: Not a git repository.")
        return 1

    # get the relative path from the repo root
    relative_path = os.path.relpath(file_path, repo_root)

    # get remote name from config if not specified
    if not hasattr(args, 'remote') or not args.remote:
        config = get_config()
        remote = config.get('default_remote', 'origin')
    else:
        remote = args.remote

    owner, repo_name, branch, repo, remote = get_repo_info(repo_root, remote)

    # determine the reference to use (branch name or commit SHA)
    ref = repo.head.commit.hexsha if args.permalink else branch

    # only check if file is pushed if not using permalink
    if not args.permalink and not is_file_pushed(repo, remote, relative_path, branch):
        print(f"Warning: File '{relative_path}' may not be pushed to the remote branch '{branch}'.")
        proceed = input("Proceed anyway? (y/n): ")
        if proceed.lower() != 'y':
            return 1

    if not check_file_exists_on_github(owner, repo_name, ref, relative_path):
        print(f"Error: File '{relative_path}' does not exist on GitHub in ref '{ref}'.")
        return 1

    line_start = None
    line_end = None

    if args.lines:
        line_parts = args.lines.split(",")
        if len(line_parts) == 1:
            line_start = int(line_parts[0])
        elif len(line_parts) == 2:
            line_start, line_end = map(int, line_parts)
        else:
            print("Error: Invalid line range format. Use 'start' or 'start,end'.")
            return 1

        # validate line numbers
        max_lines = count_file_lines(file_path)
        if max_lines > 0:
            if line_start and line_start > max_lines:
                print(f"Warning: Start line {line_start} exceeds file length ({max_lines} lines).")
                proceed = input("Proceed anyway? (y/n): ")
                if proceed.lower() != 'y':
                    return 1
            if line_end and line_end > max_lines:
                print(f"Warning: End line {line_end} exceeds file length ({max_lines} lines).")
                proceed = input("Proceed anyway? (y/n): ")
                if proceed.lower() != 'y':
                    return 1

    # convert path separators to use forward slashes for URLs
    relative_path = relative_path.replace(os.path.sep, '/')
    
    link = generate_link(owner, repo_name, ref, relative_path, line_start, line_end)
    pyperclip.copy(link)
    print(f"GitHub link copied to clipboard:")
    print(link)

    # whether to open in browser or not
    open_in_browser = getattr(args, 'open', False)
    if not open_in_browser:
        config = get_config()
        open_in_browser = config.get('open_browser', False)
        
    # open link in browser if requested
    if open_in_browser:
        print("Opening link in browser...")
        webbrowser.open(link)
    
    return 0


def main():
    """Main entry point for the CLI.
    
    Returns:
        int: Exit code
    """
    parser = argparse.ArgumentParser(
        description="Generate GitHub links for files and line numbers."
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"ghlink v{__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    init_parser = subparsers.add_parser("init", help="Initialize configuration")
    init_parser.add_argument(
        "--token", 
        help="GitHub API token (optional)"
    )
    init_parser.add_argument(
        "--remote",
        default="origin",
        help="Default Git remote to use (default: origin)"
    )
    init_parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open links in browser by default"
    )
    init_parser.add_argument(
        "--config-path",
        help="Custom path for the config file (default: ~/.config/ghlink/config)"
    )
    
    link_parser = subparsers.add_parser("link", help="Generate GitHub link (default command)")
    link_parser.add_argument(
        "file_path", 
        help="Path to the file (relative or absolute)"
    )
    link_parser.add_argument(
        "-l",
        "--lines",
        help="Line number(s) to link to. Use comma for a range (e.g., 12,16)"
    )
    link_parser.add_argument(
        "-r",
        "--remote",
        help="Git remote to use (default: from config or 'origin')"
    )
    link_parser.add_argument(
        "-p",
        "--permalink",
        action="store_true",
        help="Create a permalink using the current commit SHA instead of branch name"
    )
    link_parser.add_argument(
        "-o",
        "--open",
        action="store_true",
        help="Open the generated link in your web browser"
    )
    
    # backward compatibility for old-style usage
    parser.add_argument(
        "file_path_legacy", 
        nargs="?", 
        help=argparse.SUPPRESS
    )
    parser.add_argument("-l", "--lines-legacy", dest="lines_legacy", help=argparse.SUPPRESS)
    parser.add_argument("-r", "--remote-legacy", dest="remote_legacy", help=argparse.SUPPRESS)
    parser.add_argument("-p", "--permalink-legacy", dest="permalink_legacy", 
                        action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("-o", "--open-legacy", dest="open_legacy", 
                        action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--create-config", action="store_true", 
                       help="Create a template configuration file (deprecated, use 'init' instead)")

    args = parser.parse_args()
    
    # handle backward compatibility
    if args.create_config:
        print("Note: --create-config is deprecated, use 'ghlink init' instead")
        config_path = os.path.expanduser("~/.config/ghlink/config")
        create_config_file(config_path)
        return 0
        
    # handle legacy format (no subcommand specified)
    if not args.command and args.file_path_legacy:
        # map legacy args to new format and call cmd_link
        class LegacyArgs:
            def __init__(self):
                self.file_path = args.file_path_legacy
                self.lines = args.lines_legacy
                self.remote = args.remote_legacy
                self.permalink = args.permalink_legacy
                self.open = args.open_legacy
        
        return cmd_link(LegacyArgs())
    
    # handle specific commands
    if args.command == "init":
        return cmd_init(args)
    elif args.command == "link":
        return cmd_link(args)
    elif not args.command:
        if args.file_path_legacy:
            # already handled above with LegacyArgs
            pass

        elif len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            args.file_path = sys.argv[1]
            return cmd_link(args)
        else:
            parser.print_help()
            return 1


if __name__ == "__main__":
    sys.exit(main())
