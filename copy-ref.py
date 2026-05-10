from os import stat
import subprocess
import sys

branch = "test-dir-print"
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

diff_lines = [line for line in diff_output_process.stdout.splitlines() if line.strip()]


for line in diff_lines:
    parts = line.split("\t")

    if len(parts) < 2:
        continue

    status = parts[0]
    path = parts[-1]

    if status == "A":
        added_files.append(path)
    elif status == "M":
        modified_files.append(path)
    elif status == "D":
        deleted_files.append(path)
    elif status.startswith(("R", "C")):
        modified_files.append(path)

def build_directory_tree(paths):
    tree = {}
    for path in paths:
        normalized = path.strip().strip("/")
        if not normalized:
            continue

        parts = normalized.split("/")
        node = tree
        for dir_name in parts[:-1]:
            node = node.setdefault(dir_name, {})
        node.setdefault("__files__", set()).add(parts[-1])
    return tree


def print_tree_node(node):
    for i, obj in node.items():
        print(i)

        for j in obj:
            print(j)

def print_directory_structure(paths, label=None):
    if label:
        print(label)

    if not paths:
        print("|---(none)")
        return

    tree = build_directory_tree(paths)
    print_tree_node(tree)

print_directory_structure(added_files, "ADDED")
print_directory_structure(modified_files, "MODIFIED")
print_directory_structure(modified_files, "DELTED")
# for file in diff_output_files:
#     if "A" in file:
#         file_dir = file.replace("A::", "")
#         added_files.append(file_dir)
# 
#     if "M" in file:
#         file_dir = file.replace("M::", "")
#         modified_files.append(file)
# 
#     if "D" in file:
#         file_dir = file.replace("D::", "")
#         deleted_files.append(file)


# def get_parent_dirs(files):
#     parent_dirs = []
#     for item in files:
#         split_path = item.split("/")
#         if len(split_path) == 1:
#             if "root" not in parent_dirs:
#                 parent_dirs.append("root")
#         else:
#             parent_path = split_path[0]
#             if parent_path not in parent_dirs:
#                 parent_dirs.append(parent_path)
#     return parent_dirs


# def print_files(parent_dirs, files):
#     for parent_dir in parent_dirs:
#         print(f"{parent_dir}")
#         for file in files:
#             split_path = file.split("/")
#             if len(split_path) == 1:
#                 print(f"\n {file}")
#             else:
#                 inner_files = file.replace(f"{parent_dir}/", "")
#                 print(f"\n {inner_files}")
#         print("\n")


# added_parent_dirs = get_parent_dirs(added_files)
# modified_files_dirs = get_parent_dirs(modified_files)
# deleted_files_dirs = get_parent_dirs(deleted_files)

# print("ADDED")
# print_files(added_parent_dirs, added_files)
# print("MODIFIED")
# print_files(modified_files_dirs, modified_files)
# print("DELTED")
# print_files(deleted_files_dirs, deleted_files)
