#!/usr/bin/env python3
"""
Script to randomly change commit dates for all files in a git repository.

This script modifies the author and committer dates of all commits in the
repository to random dates within a specified range. Use with caution as this
rewrites git history.

Usage:
    python Git.py [options]

Options:
    --start-date: Start date (YYYY-MM-DD), default: 1 year ago
    --end-date: End date (YYYY-MM-DD), default: today
    --preserve-order: Keep commits in chronological order (default: False)
    --dry-run: Show what would change without making changes
"""

import subprocess
import random
from datetime import datetime, timedelta
import argparse
import sys
from pathlib import Path


def run_git_command(cmd: list, check: bool = True) -> str:
    """Execute a git command and return output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        raise


def get_all_commits() -> list:
    """Get list of all commits with their details."""
    output = run_git_command([
        'git', 'log', '--pretty=format:%H|%ai|%s'
    ])

    commits = []
    for line in output.split('\n'):
        if line:
            hash_val, date, subject = line.split('|', 2)
            commits.append({
                'hash': hash_val,
                'original_date': date,
                'subject': subject
            })

    return commits


def generate_random_dates(count: int, start_date: datetime, end_date: datetime, preserve_order: bool = False) -> list:
    """Generate random timestamps within the given range."""
    dates = []
    for _ in range(count):
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        random_seconds = random.randint(0, 86399)
        random_date = start_date + timedelta(days=random_days, seconds=random_seconds)
        dates.append(random_date)

    if preserve_order:
        dates.sort()
    else:
        random.shuffle(dates)

    return dates


def format_git_date(dt: datetime) -> str:
    """Format datetime for git command."""
    # Git date format: "Thu Nov 21 10:00:00 2024 +0000"
    return dt.strftime("%a %b %d %H:%M:%S %Y +0000")


def change_commit_date(commit_hash: str, new_date: datetime, dry_run: bool = False) -> bool:
    """Change the date of a specific commit."""
    formatted_date = format_git_date(new_date)

    env_vars = {
        'GIT_COMMITTER_DATE': formatted_date,
        'GIT_AUTHOR_DATE': formatted_date
    }

    if dry_run:
        print(f"[DRY-RUN] Would change commit {commit_hash} to {formatted_date}")
        return True

    try:
        # Use git filter-branch or git commit --amend with environment variables
        cmd = f"git filter-branch -f --env-filter 'if [ $GIT_COMMIT = {commit_hash} ] then export GIT_AUTHOR_DATE=\"{formatted_date}\"; export GIT_COMMITTER_DATE=\"{formatted_date}\"; fi' -- --all"
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error changing commit date for {commit_hash}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Randomly change commit dates in git repository'
    )
    parser.add_argument(
        '--start-date',
        default=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
        help='Start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end-date',
        default=datetime.now().strftime('%Y-%m-%d'),
        help='End date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--preserve-order',
        action='store_true',
        help='Keep commits in chronological order'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would change without making changes'
    )

    args = parser.parse_args()

    # Parse dates
    try:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    except ValueError as e:
        print(f"Error parsing dates: {e}")
        sys.exit(1)

    # Verify we're in a git repository
    try:
        run_git_command(['git', 'rev-parse', '--git-dir'])
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository")
        sys.exit(1)

    print(f"Fetching all commits...")
    commits = get_all_commits()

    if not commits:
        print("No commits found in repository")
        return

    print(f"Found {len(commits)} commits")
    print(f"Date range: {args.start_date} to {args.end_date}")
    print(f"Preserve order: {args.preserve_order}")
    print(f"Dry run: {args.dry_run}")
    print()

    if not args.dry_run:
        response = input("WARNING: This will rewrite git history. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
        print()

    # Generate random dates
    random_dates = generate_random_dates(
        len(commits),
        start_date,
        end_date,
        args.preserve_order
    )

    # Apply changes using git filter-branch
    print("Generating git filter-branch command...")

    # Build the filter-branch command with all commits
    conditions = []
    for commit, new_date in zip(commits, random_dates):
        formatted_date = format_git_date(new_date)
        conditions.append(f"if [ $GIT_COMMIT = {commit['hash']} ] then export GIT_AUTHOR_DATE='{formatted_date}'; export GIT_COMMITTER_DATE='{formatted_date}'; fi")

    # Combine all conditions
    filter_cmd = '; '.join(conditions)

    if args.dry_run:
        print("[DRY-RUN] Changes that would be applied:")
        for i, (commit, new_date) in enumerate(zip(commits[:5], random_dates[:5]), 1):
            print(f"  {i}. {commit['hash'][:7]} -> {format_git_date(new_date)}")
        if len(commits) > 5:
            print(f"  ... and {len(commits) - 5} more commits")
    else:
        try:
            print("Rewriting history...")
            full_cmd = f"git filter-branch -f --env-filter '{filter_cmd}' -- --all"
            subprocess.run(full_cmd, shell=True, check=True)
            print("✓ Successfully updated commit dates")
            print("\nChanges applied:")
            for i, (commit, new_date) in enumerate(zip(commits[:10], random_dates[:10]), 1):
                print(f"  {i}. {commit['hash'][:7]} -> {format_git_date(new_date)}")
            if len(commits) > 10:
                print(f"  ... and {len(commits) - 10} more commits")
        except subprocess.CalledProcessError as e:
            print(f"Error rewriting history: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
