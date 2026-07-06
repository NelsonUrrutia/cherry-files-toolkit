# Cherry Files Toolkit

> A terminal UI (built with [Textual](https://textual.textualize.io/)) for moving
> work between git branches at the **file** level — pick the final state of the
> files you want and apply them to another branch as one clean commit, no
> commit-by-commit cherry-picking.

It ships two tools side by side:

- **Cherry Files Picker** — select files from your current branch and commit
  their current content onto a target branch.
- **Cherry Files Diff** — see every file added, modified, or deleted on a
  branch since it diverged from its base, grouped as a scannable tree.

## The idea

This project is a new iteration of my previous
[Cherry Files Picker](https://github.com/NelsonUrrutia/cherry-files-picker).
The goal is the same — move the final state of selected files between branches
as one clean commit — but this version upgrades the UI to a full TUI and adds
a second module, **Cherry Files Diff**, for understanding branch divergence at
a glance.

## Install

```bash
pip install cherry-files-toolkit
```

Requires Python 3.10+ and `git` on your PATH.

## Usage

Run it from inside any git repository:

```bash
cherry-files-toolkit
```

Press `Ctrl+Q` to quit.

### Cherry Files Picker (right panel)

Transfers the final approved state of selected files from your working branch
to another branch:

1. **Source branch** is pre-filled with your current branch.
2. Pick a **target branch** — where the work should land.
3. Search and select the **files** to move. Selections persist while you
   filter.
4. Write a **commit title and description**, review the selected files, and
   hit **Cherry Pick Files**. The toolkit commits those files' current
   content onto the target branch in a single commit.

Use it when you know which files are done and want them on another branch
without replaying the messy commit history that produced them.

### Cherry Files Diff (left panel)

Explains branch divergence at the file level, so you can recover context on a
branch you don't know well:

1. Pick the **divergent branch** (the one with the work) and its **base
   branch**.
2. **Start Diff Checker** finds the point where they diverged and lists every
   file created, modified, or deleted since — with per-category counts and a
   directory tree for fast scanning.

## License

[MIT](LICENSE)
