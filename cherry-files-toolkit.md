# Cherry Files Toolkit — Requirements & Implementation Checklist

## Overview

Two separate bash CLI tools that together form a git file workflow toolkit:

| Tool                  | Command                                                              | Purpose                                                                                                          |
| --------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `cherry-files-diff`   | `cherry-files-diff [branch] [--base <branch>] [--tree] [--no-color]` | Show all files changed on a branch vs a base, grouped by folder                                                  |
| `cherry-files-picker` | `cherry-files-picker`                                                | Interactive TUI to cherry-pick specific files from a source branch into a target branch as a single clean commit |

1. Now — Python: Enhance cherry-files-picker with the diff integration (show changed files as a selectable list, manual entry below). Publish to PyPI when ready.
2. Later — Bash: Rewrite as a learning exercise, zero deps, distribution-friendly single file.
3. Incorporate the search commit by title `git log --grep="commit title"`

---

## Tool 1 — cherry-files-diff

### What it is

Already built. Currently installed at `~/.local/bin/branch-diff`. Needs to be renamed.

### Requirements

- [ ] Rename `~/.local/bin/branch-diff` → `~/.local/bin/cherry-files-diff`
- [ ] Update the name in the script's header comment and usage line

### Flags (already implemented)

- `[branch]` — branch to inspect (default: current branch)
- `--base <branch>` — branch to compare against (default: `main`)
- `--tree` — output as a file tree
- `--no-color` — disable color (auto-disabled when piping)
- `-h, --help` — show help

---

## Tool 2 — cherry-files-picker

### What it is

A bash rewrite of the existing Python `cherry-files-picker` tool, enhanced with a `gum` TUI and integrated diff-based file selection.

### Dependencies

- `gum` by Charmbracelet — `brew install gum`
- Script must check for `gum` on startup and print install instructions if missing

### Install location

`~/.local/bin/cherry-files-picker`

---

## cherry-files-picker — Detailed Requirements

### Startup

- [ ] Check `gum` is installed; print `brew install gum` and exit 1 if not
- [ ] Check we're inside a git repo; styled error + exit 1 if not
- [ ] Display branded header using `gum style --border rounded`

---

### Step 1 — Branch Settings

- [ ] Show section header: `── 1. BRANCH SETTINGS ──`
- [ ] **Source branch** — `gum choose` from `git branch --list` output
- [ ] **Base branch** — `gum choose` with `main` pre-highlighted (used for diff computation)
- [ ] **Target branch** — `gum choose` from branch list
- [ ] Guard: source branch ≠ target branch; show error and exit 1 if equal

---

### Step 2 — File Selection

- [ ] Show section header: `── 2. FILE SELECTION ──`

**Part A — From diff (primary)**

- [ ] Compute merge base: `git merge-base "$BASE" "$SOURCE"`
- [ ] Get changed file list: `git diff --name-only "$MERGE_BASE".."$SOURCE"`
- [ ] If files exist: present with `gum choose --no-limit` (SPACE to toggle, ENTER to confirm)
- [ ] If no files in diff: show a notice and skip to Part B

**Part B — Manual entry (secondary, optional)**

- [ ] Show prompt explaining optional manual additions
- [ ] Loop: `gum input --placeholder "File path (leave blank to finish)"`
- [ ] Stop loop on empty input
- [ ] Append manual entries to selected list; skip duplicates

**Validation**

- [ ] Guard: at least 1 file must be selected total; show error and exit 1 if none

---

### Step 3 — Commit Settings

- [ ] Show section header: `── 3. COMMIT SETTINGS ──`
- [ ] **Commit title** — `gum input`, re-prompt if blank (required)
- [ ] **Commit description** — `gum input`, re-prompt if blank (required)

---

### Step 4 — Summary

- [ ] Show section header: `── SUMMARY ──`
- [ ] Display source branch, base branch, target branch
- [ ] List all selected files (bulleted)
- [ ] Display commit title and description

---

### Step 5 — Confirm

- [ ] `gum confirm "Continue with merge?"`
- [ ] On cancel: print "Merge cancelled." and exit 0

---

### Step 6 — Execute

- [ ] Create a temp directory (`mktemp -d`) for staging file contents
- [ ] For each selected file: `git show "$SOURCE:$file" > "$TMPDIR/<index>"` (reads from source branch without switching)
- [ ] `git checkout "$TARGET"`
- [ ] For each file: `mkdir -p "$(dirname "$file")"` + copy from temp
- [ ] `git add -A`
- [ ] `git commit -m "$TITLE" -m "$DESC" -m "Source branch: $SOURCE"`
- [ ] Clean up temp directory
- [ ] Display styled success message

---

## Edge Cases

| Scenario                            | Expected behavior                                         |
| ----------------------------------- | --------------------------------------------------------- |
| `gum` not installed                 | Error with `brew install gum` instructions, exit 1        |
| Not in a git repo                   | Styled error, exit 1                                      |
| Source == Target branch             | Error "Source and target must be different", exit 1       |
| No files in diff                    | Skip Part A, go straight to manual entry                  |
| No files selected at all            | Error "No files selected", exit 1                         |
| Blank commit title or description   | Re-prompt until non-empty                                 |
| User cancels at confirm             | "Merge cancelled." exit 0                                 |
| File doesn't exist on source branch | `git show` will error; catch and report which file failed |

---

## Verification

```bash
# Tool 1
cherry-files-diff --help                         # check renamed correctly
cherry-files-diff --base main                    # verify output unchanged

# Tool 2 — happy path
cd ~/Documents/GitHub/Retheme-Half-Magic
cherry-files-picker
# 1. Select source: euphoria-collab-launch
# 2. Select base: main
# 3. Select target: stage
# 4. Pick files from diff checkboxes
# 5. Add one manual file path
# 6. Enter commit title + description
# 7. Confirm → check git log on stage shows new commit

# Tool 2 — cancel
cherry-files-picker   # proceed to confirm step → select No → exits cleanly

# Tool 2 — no gum
# Temporarily: mv $(which gum) /tmp/gum_bak
cherry-files-picker   # should print install instructions
# mv /tmp/gum_bak back
```
