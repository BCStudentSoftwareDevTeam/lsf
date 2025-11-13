# PR Description Generator

This script automatically generates a pull request description based on your git changes.

## Usage

From the root of the repository, run:

```bash
python3 scripts/generate_pr_description.py [base_branch]
```

### Parameters

- `base_branch` (optional): The branch to compare against. Default is `main`.

### Examples

1. Generate PR description comparing to main branch:
```bash
python3 scripts/generate_pr_description.py
```

2. Generate PR description comparing to a specific branch:
```bash
python3 scripts/generate_pr_description.py develop
```

3. Generate PR description comparing to a specific commit:
```bash
python3 scripts/generate_pr_description.py d5dd4d1
```

## Output

The script will generate a formatted PR description that includes:

- **Summary of Changes**: List of commit messages
- **Changed Files**: Organized by category (Models, Controllers, Templates, etc.)
- **Statistics**: Overall diff statistics (files changed, insertions, deletions)

### File Categories

The script automatically categorizes changed files into:

- **Models**: Files in `app/models/`
- **Controllers**: Files in `app/controllers/`
- **Templates**: Files in `app/templates/`
- **Static Files**: Files in `app/static/`
- **Tests**: Files in `tests/`
- **Scripts**: Files in `scripts/`
- **Database**: Files in `database/`
- **Documentation**: Markdown files (`.md`)
- **Configuration**: `requirements.txt`, `setup.sh`, `app.py`
- **Other**: Any other files

## Redirection to File

You can save the output to a file:

```bash
python3 scripts/generate_pr_description.py > pr_description.md
```

## Integration with GitHub

Copy the output and paste it into your PR description on GitHub. The markdown formatting will be preserved.

## Requirements

- Git repository
- Python 3.x
- Standard subprocess module (included in Python)

## Troubleshooting

**Error: "Not in a git repository"**
- Make sure you're running the script from within a git repository

**Error: "Not a valid object name"**
- The base branch doesn't exist. Try specifying a different base branch or commit

**No changes detected**
- Make sure you've committed your changes
- Verify you're comparing to the correct base branch
- Try specifying a different base commit/branch
