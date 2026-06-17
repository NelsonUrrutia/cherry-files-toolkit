# Git Path-Specific Checkout

## What is it?

`git checkout` has two modes:

- **Switch branches:** `git checkout <branch>` — moves your entire working tree to that branch.
- **Restore files from another branch:** `git checkout <branch> -- <file1> <file2>` — copies specific files from that branch into your current working tree **without switching branches**. The files are already staged and ready to commit.

The `--` tells git: "everything after this is a file path, not a branch name."

## Example

```bash
# You're on "main", want to bring files from "feature"
git checkout main
git checkout feature -- src/app.py src/utils.py

# src/app.py and src/utils.py now have the content from "feature"
# You're still on "main", and the files are already staged
git commit -m "Cherry pick files from feature"
```

## Modern alternative (Git 2.23+)

In newer git versions, these two modes were split into separate commands for clarity:

- `git switch <branch>` — switch branches
- `git restore --source=<branch> -- <file>` — restore files from another branch

Same operation, just clearer naming.

## Why it matters

This eliminates the need to manually read file contents, switch branches, and write files back using a scripting language. Git handles it natively, including edge cases like binary files, file permissions, and deleted files.
