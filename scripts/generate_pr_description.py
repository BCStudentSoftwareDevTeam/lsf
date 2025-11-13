#!/usr/bin/env python3
"""
Script to generate PR descriptions based on git changes.
Usage: python scripts/generate_pr_description.py [base_branch]
"""

import subprocess
import sys
import re
from collections import defaultdict


def run_git_command(command):
    """Run a git command and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}", file=sys.stderr)
        print(f"Error: {e.stderr}", file=sys.stderr)
        return ""


def get_current_branch():
    """Get the current git branch name."""
    return run_git_command("git rev-parse --abbrev-ref HEAD")


def get_commit_messages(base_branch="main"):
    """Get commit messages from current branch compared to base branch."""
    current_branch = get_current_branch()
    if not current_branch:
        return []
    
    # Try to find common ancestor
    merge_base = run_git_command(f"git merge-base {base_branch} {current_branch}")
    if not merge_base:
        # Fallback to comparing with base branch directly
        command = f"git log {base_branch}..HEAD --pretty=format:%s"
    else:
        command = f"git log {merge_base}..HEAD --pretty=format:%s"
    
    output = run_git_command(command)
    if not output:
        return []
    
    return [msg for msg in output.split('\n') if msg.strip()]


def get_changed_files(base_branch="main"):
    """Get list of changed files compared to base branch."""
    current_branch = get_current_branch()
    if not current_branch:
        return []
    
    # Try to find common ancestor
    merge_base = run_git_command(f"git merge-base {base_branch} {current_branch}")
    if not merge_base:
        command = f"git diff --name-status {base_branch}...HEAD"
    else:
        command = f"git diff --name-status {merge_base}..HEAD"
    
    output = run_git_command(command)
    if not output:
        return []
    
    files = []
    for line in output.split('\n'):
        if line.strip():
            parts = line.split('\t', 1)
            if len(parts) == 2:
                status, filename = parts
                files.append((status, filename))
    
    return files


def categorize_changes(changed_files):
    """Categorize changed files by type."""
    categories = defaultdict(list)
    
    for status, filepath in changed_files:
        # Determine category based on file path
        if filepath.startswith('app/models/'):
            categories['Models'].append((status, filepath))
        elif filepath.startswith('app/controllers/'):
            categories['Controllers'].append((status, filepath))
        elif filepath.startswith('app/templates/'):
            categories['Templates'].append((status, filepath))
        elif filepath.startswith('app/static/'):
            categories['Static Files'].append((status, filepath))
        elif filepath.startswith('tests/'):
            categories['Tests'].append((status, filepath))
        elif filepath.startswith('scripts/'):
            categories['Scripts'].append((status, filepath))
        elif filepath.startswith('database/'):
            categories['Database'].append((status, filepath))
        elif filepath.endswith('.md'):
            categories['Documentation'].append((status, filepath))
        elif filepath in ['requirements.txt', 'setup.sh', 'app.py']:
            categories['Configuration'].append((status, filepath))
        else:
            categories['Other'].append((status, filepath))
    
    return categories


def get_diff_stats(base_branch="main"):
    """Get diff statistics."""
    current_branch = get_current_branch()
    if not current_branch:
        return "", ""
    
    merge_base = run_git_command(f"git merge-base {base_branch} {current_branch}")
    if not merge_base:
        command = f"git diff --shortstat {base_branch}...HEAD"
    else:
        command = f"git diff --shortstat {merge_base}..HEAD"
    
    stats = run_git_command(command)
    return stats


def format_status(status):
    """Format status code to human readable."""
    status_map = {
        'A': 'Added',
        'M': 'Modified',
        'D': 'Deleted',
        'R': 'Renamed',
        'C': 'Copied'
    }
    return status_map.get(status[0], status)


def generate_pr_description(base_branch="main"):
    """Generate a PR description based on git changes."""
    current_branch = get_current_branch()
    
    # Check if base branch exists
    check_base = run_git_command(f"git rev-parse --verify {base_branch} 2>/dev/null")
    if not check_base:
        print(f"Warning: Base branch '{base_branch}' not found. Using HEAD~1 as base.", file=sys.stderr)
        base_branch = "HEAD~1"
    
    print("# Pull Request Description\n")
    print(f"**Branch:** `{current_branch}`")
    print(f"**Base:** `{base_branch}`\n")
    
    # Get commit messages
    commits = get_commit_messages(base_branch)
    if commits:
        print("## Summary of Changes\n")
        print("This PR includes the following commits:\n")
        for commit in commits:
            print(f"- {commit}")
        print()
    
    # Get changed files
    changed_files = get_changed_files(base_branch)
    if changed_files:
        print("## Changed Files\n")
        categories = categorize_changes(changed_files)
        
        for category, files in sorted(categories.items()):
            print(f"### {category}")
            for status, filepath in files:
                status_text = format_status(status)
                print(f"- **{status_text}**: `{filepath}`")
            print()
    
    # Get diff stats
    stats = get_diff_stats(base_branch)
    if stats:
        print(f"## Statistics\n")
        print(f"{stats}\n")
    
    if not commits and not changed_files:
        print("**No changes detected compared to base branch.**\n")
        print("Please ensure you have committed your changes and that the base branch is correct.")


def main():
    """Main function."""
    base_branch = sys.argv[1] if len(sys.argv) > 1 else "main"
    
    # Check if we're in a git repository
    result = subprocess.run(
        "git rev-parse --git-dir",
        shell=True,
        capture_output=True
    )
    
    if result.returncode != 0:
        print("Error: Not in a git repository", file=sys.stderr)
        sys.exit(1)
    
    generate_pr_description(base_branch)


if __name__ == "__main__":
    main()
