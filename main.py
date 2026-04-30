import subprocess
import sys

branch = "migration-bash-to-python"
base = "main"
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
        file_dir = file.replace("A::", "")
        added_files.append(file_dir)

    if "M" in file:
        file_dir = file.replace("M::", "")
        modified_files.append(file)

    if "D" in file:
        file_dir = file.replace("D::", "")
        deleted_files.append(file)


def get_parent_dirs(files):
    parent_dirs = []
    for item in files:
        split_path = item.split("/")
        if len(split_path) == 1:
            if "root" not in parent_dirs:
                parent_dirs.append("root")
        else:
            parent_path = split_path[0]
            if parent_path not in parent_dirs:
                parent_dirs.append(parent_path)
    return parent_dirs


def print_files(parent_dirs, files):
    for parent_dir in parent_dirs:
        print(f"{parent_dir}")
        for file in files:
            split_path = file.split("/")
            if len(split_path) == 1:
                print(f"\n {file}")
            else:
                inner_files = file.replace(f"{parent_dir}/", "")
                print(f"\n {inner_files}")
        print("\n")


added_parent_dirs = get_parent_dirs(added_files)
modified_files_dirs = get_parent_dirs(modified_files)
deleted_files_dirs = get_parent_dirs(deleted_files)

print("ADDED")
print_files(added_parent_dirs, added_files)
print("MODIFIED")
print_files(modified_files_dirs, modified_files)
print("DELTED")
print_files(deleted_files_dirs, deleted_files)
