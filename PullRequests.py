#!/usr/bin/env python3
"""Create and close a batch of pull requests for the current repository."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class PullRequestRecord:
    """Track the branch and pull request created by the script."""

    branch_name: str
    number: int
    url: str


def run_command(command: list[str], check: bool = True) -> str:
    """Run a command and return stdout."""
    result = subprocess.run(command, capture_output=True, text=True)

    if check and result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        message = stderr or stdout or f"Command failed with exit code {result.returncode}"
        raise RuntimeError(f"{' '.join(command)}\n{message}")

    return result.stdout.strip()


def ensure_git_repository() -> None:
    """Abort if the current directory is not inside a git repository."""
    run_command(["git", "rev-parse", "--show-toplevel"])


def ensure_clean_worktree() -> None:
    """Abort when local changes would make branch switching unsafe."""
    status_output = run_command(["git", "status", "--porcelain"])
    if status_output:
        raise RuntimeError("Working tree is not clean. Commit or stash changes before running this script.")


def ensure_gh_authenticated() -> None:
    """Abort if the GitHub CLI is unavailable or unauthenticated."""
    run_command(["gh", "auth", "status"])


def get_current_branch() -> str:
    """Return the currently checked out branch."""
    branch_name = run_command(["git", "branch", "--show-current"])
    if not branch_name:
        raise RuntimeError("Could not determine the current git branch.")
    return branch_name


def detect_base_branch() -> str:
    """Infer the repository's default branch from origin/HEAD when available."""
    remote_head = run_command(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], check=False)

    if remote_head:
        return remote_head.rsplit("/", maxsplit=1)[-1]

    return get_current_branch()


def print_plan(args: argparse.Namespace, base_branch: str, repo_flag: list[str]) -> None:
    """Print the effective configuration before making changes."""
    print(f"Count: {args.count}")
    print(f"Base branch: {base_branch}")
    print(f"Branch prefix: {args.branch_prefix}")
    print(f"Delete remote branches: {not args.keep_remote_branches}")
    print(f"Delete local branches: {not args.keep_local_branches}")
    print(f"Dry run: {args.dry_run}")
    if repo_flag:
        print(f"GitHub repo override: {args.repo}")
    print()


def create_branch(branch_name: str, base_branch: str, dry_run: bool) -> None:
    """Create a branch from the base branch and add an empty commit."""
    commit_message = f"chore: seed PR {branch_name}"

    if dry_run:
        print(f"[DRY-RUN] git checkout {base_branch}")
        print(f"[DRY-RUN] git checkout -b {branch_name} {base_branch}")
        print(f"[DRY-RUN] git commit --allow-empty -m \"{commit_message}\"")
        print(f"[DRY-RUN] git push -u origin {branch_name}")
        return

    run_command(["git", "checkout", base_branch])
    run_command(["git", "checkout", "-b", branch_name, base_branch])
    run_command(["git", "commit", "--allow-empty", "-m", commit_message])
    run_command(["git", "push", "-u", "origin", branch_name])


def create_pull_request(
    branch_name: str,
    base_branch: str,
    repo_flag: list[str],
    dry_run: bool,
) -> PullRequestRecord:
    """Open a pull request for the branch and return its metadata."""
    title = f"Test PR: {branch_name}"
    body = f"Automated test pull request created by PullRequests.py for branch {branch_name}."

    if dry_run:
        print(
            f"[DRY-RUN] gh pr create --base {base_branch} --head {branch_name} "
            f"--title \"{title}\" --body \"{body}\" {' '.join(repo_flag)}"
        )
        return PullRequestRecord(branch_name=branch_name, number=0, url="dry-run")

    run_command(
        [
            "gh",
            "pr",
            "create",
            "--base",
            base_branch,
            "--head",
            branch_name,
            "--title",
            title,
            "--body",
            body,
            *repo_flag,
        ]
    )

    details = run_command(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--head",
            branch_name,
            "--limit",
            "1",
            "--json",
            "number,url",
            *repo_flag,
        ]
    )

    payload = json.loads(details)
    if not payload:
        raise RuntimeError(f"Failed to find the pull request for branch {branch_name} after creation.")

    return PullRequestRecord(
        branch_name=branch_name,
        number=payload[0]["number"],
        url=payload[0]["url"],
    )


def close_pull_request(
    record: PullRequestRecord,
    repo_flag: list[str],
    keep_remote_branches: bool,
    dry_run: bool,
) -> None:
    """Close the pull request and optionally remove the remote branch."""
    if dry_run:
        print(f"[DRY-RUN] gh pr close {record.number or '<pending>'} --comment \"Closing automated test PR.\" {' '.join(repo_flag)}")
        if not keep_remote_branches:
            print(f"[DRY-RUN] git push origin --delete {record.branch_name}")
        return

    run_command(
        [
            "gh",
            "pr",
            "close",
            str(record.number),
            "--comment",
            "Closing automated test PR.",
            *repo_flag,
        ]
    )

    if not keep_remote_branches:
        run_command(["git", "push", "origin", "--delete", record.branch_name])


def delete_local_branch(branch_name: str, dry_run: bool) -> None:
    """Delete a local branch after the PR is closed."""
    if dry_run:
        print(f"[DRY-RUN] git branch -D {branch_name}")
        return

    run_command(["git", "branch", "-D", branch_name])


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create and then close a batch of pull requests for the current repository."
    )
    parser.add_argument("--count", type=int, default=5, help="Number of pull requests to create. Default: 5")
    parser.add_argument(
        "--base-branch",
        help="Base branch for new PRs. Default: detect from origin/HEAD or use current branch.",
    )
    parser.add_argument(
        "--branch-prefix",
        default="automation/pr-cycle",
        help="Prefix for generated branch names.",
    )
    parser.add_argument("--repo", help="Optional GitHub repo override in OWNER/REPO format.")
    parser.add_argument(
        "--keep-local-branches",
        action="store_true",
        help="Keep the local branches after the PRs are closed.",
    )
    parser.add_argument(
        "--keep-remote-branches",
        action="store_true",
        help="Keep the remote branches after the PRs are closed.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the actions without changing git or GitHub state.",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point."""
    args = parse_args()

    if args.count < 1:
        print("Error: --count must be at least 1.", file=sys.stderr)
        return 1

    ensure_git_repository()
    if not args.dry_run:
        ensure_clean_worktree()
        ensure_gh_authenticated()

    original_branch = get_current_branch()
    base_branch = args.base_branch or detect_base_branch()
    repo_flag = ["--repo", args.repo] if args.repo else []
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    created_prs: list[PullRequestRecord] = []

    print_plan(args, base_branch, repo_flag)

    try:
        for index in range(1, args.count + 1):
            branch_name = f"{args.branch_prefix}-{timestamp}-{index:02d}"
            print(f"Creating PR {index}/{args.count}: {branch_name}")
            create_branch(branch_name, base_branch, args.dry_run)
            record = create_pull_request(branch_name, base_branch, repo_flag, args.dry_run)
            created_prs.append(record)
            print(f"Created PR for {branch_name}: #{record.number} {record.url}")
            print()

        print("Closing created pull requests...")
        if args.dry_run:
            print(f"[DRY-RUN] git checkout {base_branch}")
        else:
            run_command(["git", "checkout", base_branch])

        for record in created_prs:
            close_pull_request(record, repo_flag, args.keep_remote_branches, args.dry_run)
            if not args.keep_local_branches:
                delete_local_branch(record.branch_name, args.dry_run)
            print(f"Closed PR for {record.branch_name}: #{record.number} {record.url}")

    finally:
        if not args.dry_run:
            run_command(["git", "checkout", original_branch], check=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())