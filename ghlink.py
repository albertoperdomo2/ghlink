import argparse
import os
import sys
from git import Repo, InvalidGitRepositoryError
import requests


def get_repo_info(repo_path):
    try:
        repo = Repo(repo_path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        print("Error: Not a git repository.")
        sys.exit(1)

    try:
        remote_url = repo.remote().url
    except AttributeError:
        print("Error: No remote 'origin' set.")
        sys.exit(1)

    # extract owner and repo name from the remote URL
    parts = remote_url.split(":")[-1].split("/")
    owner = parts[-2]
    repo_name = parts[-1].replace(".git", "")

    branch = repo.active_branch.name
    return owner, repo_name, branch, repo


def is_file_pushed(repo, file_path, branch):
    try:
        commit = repo.head.commit
        remote_commit = repo.remotes.origin.refs[branch].commit
        if commit != remote_commit:
            return False

        # check if the file exists in the remote branch
        remote_tree = remote_commit.tree
        try:
            remote_tree[file_path]
            return True
        except KeyError:
            return False
    except Exception:
        return False


def generate_link(owner, repo_name, branch, file_path, line_start, line_end=None):
    base_url = f"https://github.com/{owner}/{repo_name}/blob/{branch}/{file_path}"

    if line_start and line_end:
        return f"{base_url}#L{line_start}-L{line_end}"
    elif line_start:
        return f"{base_url}#L{line_start}"
    else:
        return base_url


def get_github_token():
    return os.environ.get("GITHUB_TOKEN")


def check_file_exists_on_github(owner, repo_name, branch, file_path):
    token = get_github_token()
    if not token:
        print("Warning: GITHUB_TOKEN not set. Rate limiting may occur.")

    headers = {"Authorization": f"token {token}"} if token else {}
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}?ref={branch}"

    response = requests.get(url, headers=headers)
    return response.status_code == 200


def main():
    parser = argparse.ArgumentParser(
        description="Generate GitHub links for files and line numbers."
    )
    parser.add_argument("file_path", help="Path to the file (relative or absolute)")
    parser.add_argument(
        "-l",
        "--lines",
        help="Line number(s) to link to. Use comma for a range (e.g., 12,16)",
    )

    args = parser.parse_args()

    # get the absolute path of the file
    file_path = os.path.abspath(args.file_path)

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    # get the repo root directory
    try:
        repo = Repo(file_path, search_parent_directories=True)
        repo_root = repo.git.rev_parse("--show-toplevel")
    except InvalidGitRepositoryError:
        print("Error: Not a git repository.")
        sys.exit(1)

    # get the relative path from the repo root
    relative_path = os.path.relpath(file_path, repo_root)

    owner, repo_name, branch, repo = get_repo_info(repo_root)

    if not is_file_pushed(repo, relative_path, branch):
        print(
            f"Error: File '{relative_path}' is not pushed to the remote branch '{branch}'."
        )
        sys.exit(1)

    if not check_file_exists_on_github(owner, repo_name, branch, relative_path):
        print(
            f"Error: File '{relative_path}' does not exist on GitHub in branch '{branch}'."
        )
        sys.exit(1)

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
            sys.exit(1)

    link = generate_link(owner, repo_name, branch, relative_path, line_start, line_end)
    print(link)


if __name__ == "__main__":
    main()
