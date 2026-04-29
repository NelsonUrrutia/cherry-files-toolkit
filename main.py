import subprocess
import sys

branch = "euphoria-collab-launch"
base = "stage"
added_files = []
modified_files = []
deleted_files = []


# Guard must be inside a git repo
git_dir_process = subprocess.run(
    ["git", "rev-parse", "--git-dir"], capture_output=True, text=True
)
git_dir_process_return_code = git_dir_process.returncode

if git_dir_process_return_code != 0:
    print("Not inside a git repository")
    sys.exit()

merge_base_process = subprocess.run(
    ["git", "merge-base", base, branch], capture_output=True, text=True
)
merge_base_commit = merge_base_process.stdout.replace("\n", "")

merge_base_short = merge_base_commit[0:8:1]


diff_output_process = subprocess.run(
    ["git", "diff", "--name-status", f"{merge_base_commit}..{branch}"],
    capture_output=True,
    text=True,
)

diff_output_files = diff_output_process.stdout.replace("\t", "::").split("\n")

for file in diff_output_files:
    if "A" in file:
        added_files.append(file)

    if "M" in file:
        modified_files.append(file)

    if "D" in file:
        deleted_files.append(file)

print("ADDED")
print(added_files)
print("--\n")

print("MODIFIED")
print(modified_files)
print("--\n")

print("DELETED")
print(deleted_files)
