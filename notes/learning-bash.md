# Learning bash

## Guard: must be inside a git

> Lines 69 - 73

Breakdown:

- `if ! ...`

  The `!` negates the exit code. So the `if` blocks run only when
  the command fails.

- `git rev-parse --git-dir`

  Tries to locate the `.git` directory of the current repo.
  It succeeds (exit code 0) if you're inside a git repo,
  and fails (exit code 1) if you're not.
  - `rev-parse`

    Is an ancillary "plumbing" command used primarily to
    translate human-readable Git references.

  - `--git-dir`
    Show `$GIT_DIR` if defined. Otherwise show the path to
    the .git directory. If `$GIT_DIR` is not defined and
    the current directory is not detected to lie in a Git
    repository or work tree print a message to `strderr` and
    exit with nonzero status.

    > Example of error output
    > `fatal: not a git repository (or any of the parent directories): .git`

- `&>/dev/null`

  Redirects both `stdout` and `stderr` to `/dev/null`,
  silencing any output - we only care about the exit code,
  not the message.
  - `&>`
    This is a **redirection operator** that redirect both
    `stdout` and `stderr` at the same time.
    It's a shorthand for `1>file 2>&2` (first redirects to
    `stdout`, the redirect `stderr` to wherever `stdout` is going).
    - 1 = `stdout` (normal output)
    - 2 = `stderr` (error output)
    - &> = both at once
  - `/dev/null`
    This is a special file on Unix/Linux systems nicknamed the "black hole".
    Anything written to it is permanently discarded.

  In this specific case, the script only case about whether the command
  succeeded or failed (the exit code), not about what it printed.
  So all output is thrown away to keep the terminal clean and silent

- `exit 1`

  Terminates the script with exit code `1`, signaling failure to the caller.

## Parse arguments

> Lines 75 - 98

Breakdown:

1. Initialize default variables - BRANCH, BASE, TREE, skip_next
2. Loop over all script arguments (`$@`), storing each one temporarily in `arg`
3. At the start of each iteration, check if skip_next is true:

- If yes -> this `arg` is the value for --base, so assign it to BASE,
  reset skip_next = false, and skip the rest of the iteration (continue)

- If no -> proceed to the case

1. The case matches the current argument:

- --no-color, --help, -h -> do nothing handled elsewhere
- --tree -> set TREE = true
- --base -> set skip_next = true so the next iteration captures the vale into BASE
- Anything else (\*) -> if BRANCH is still empty, assign this `arg` to BRANCH

## Guard branches

> Lines 100 - 126

The function checks if a branch exists either locally or remotely.
Then the script uses it to validate both $BRANCH and $BASE before doing any real
work, and ensures they aren't the same branch.

### Bash function

```bash
branch_exists(){
  ...
}
```

In bash, functions are defined like this - no parameters are declared in the parentheses
(they're always empty). Arguments are accessed inside via $1, $2, $3, etc.,
just like script arguments

`branch_exists "&BRANCH" <- this becomes $1 inside the function`

The function returns an exit code, not a value.

- 0 -> success/true
- 1 -> failure/false

That is why it works with `if ! branch_exists "$BRANCH` it's checking the exit code,
not a return value.

### The Git command

- `git show-ref --verify --quiet "refs/heads/$1"`
  - `git show-ref` -> checks if a reference exists in the repo
  - `--veriy` -> ensures it's an exact, valid ref
  - `--quiet` -> suppresses output
  - `refs/heads/$1` is the path for local branches.

- `git show-ref --verify --quiet "refs/remotes/origin/$1"`
  - Same thing but checks remote branches.

- Joined with `||` meaning: "exists locally OR exists on remote"

### The Guard

- Guard 1 & 2, branch existence
- Guard 3, branch vs base. Prevents comparing a branch against itself.

### Find divergence print

> Lines 129 - 138

This blocks finds the exact commit where `$BRANCH` split off
from `$BASE`, store a short version of its hash, and prints
the summary header to the terminal.

`git merge-base BRANCH BASE`

The git command to find the common ancestor commit, the point
where the two branches diverged.
Returns the commit hash.

`MERGE_BASE_SHORT = "${MERGE_BASE:0:0}"`

Then shorten the hash, by taking the first 8 characters

### Get all changed file

> Lines 141 - 146

Get the list of files that changed between the divergence point
and the tip of `$BRANCH`. If there is nothing, tell the user
exit cleanly.

`git diff` compares two points in git history and shows what changed.

`--name-status` limits the output to just the file name and its
status letter, instead of showing the full line-by-line diff.

`M -> Modified
A -> Discarded
D -> Deleted
R -> Renamed`

### Parse into buckets

> Lines 148 - 157

Takes the raw diff output, split into three separate lists by status
(Added, Modified, Deleted) count each one and sum them into total.

`awk` is a text processing tool built into UNIX/Linux systems.
Programming language designed specifically for processing structured
text line by line. In `awk`, columns are automatically split by white
space and references as `$1`, `$2`.

In each `awk` command is saying:

> If the first column is A, print the second column.

### Tree output

> Lines 166 - 209

Takes a flat list of files, groups them by their top-level folder,
then prints everything as a nested tree using box-drawing characters
— handling the last item at each level specially to use └── instead of ├──.

### Group output

> Lines 212 - 232

Same logic as the function as `print_as_tree` for grouping files
by folder but instead of calculating three characters uses a
simple indentation.

### Print result

> Lines 234 - 270
