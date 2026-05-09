# cherry-files-toolkit

## Flow `cherry-files-picker`

Cherry Files Picker transfers the final approved state of selected files from someone
branch into another.
For Cherry Files Picker, the user intent is:

- “Show me the files whose current content differs from the target context.”
- “Let me choose the final versions I want.”
- “Apply those final versions as one clean result.”

### 1. Select branches

- The user selects a `source branch`
  The `source branch` is the branch where the user worked: created or modified
  files.

- The user selects a `target branch`
  The `target branch` is the branch where the user wants to move/merge the work.

### 2. Select files

- The user selects all the files that wants to move/merge to the `target branch`

### 3. Create commit title and description

- The user sets a commit title and description
- The user reviews the files to commit

### 4. Commit

- The user accepts the commit and the script starts with the commit and merging process

## Flow `cherry-files-diff`

Cherry Files Diff explains branch divergence at the file level, so someone without
prior context can quickly understand what changed since the branch split.

For Cherry Files Diff, the user intent is:

- “I don’t know this branch well.”
- “Show me what was added, modified, and deleted since it diverged from base.”
- “Group it in a way I can scan fast and recover context.”

### 1. Set branches

- The user selects a `divergent branch`
  This could be the current working branch or other.
- The user selects the `base branch`
  This is the base branch where the divergent branch was based on.

### 2. List of added, modified and deleted files

- The script shows all the added, modified and deleted files since
  since the point where the divergent and based branch diverged.
