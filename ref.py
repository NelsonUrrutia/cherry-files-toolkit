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
    # For renames/copies git outputs: "R100\told\tnew" (or "C100\told\tnew").
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


def _print_tree_node(node, prefix=""):
    directories = sorted([name for name in node.keys() if name != "__files__"])
    files = sorted(node.get("__files__", set()))

    entries = [(name, "dir") for name in directories] + [(name, "file") for name in files]
    for idx, (name, kind) in enumerate(entries):
        is_last = idx == len(entries) - 1
        connector = "└── " if is_last else "├── "

        if kind == "dir":
            print(f"{prefix}{connector}{name}/")
            child_prefix = prefix + ("    " if is_last else "│   ")
            _print_tree_node(node[name], prefix=child_prefix)
        else:
            print(f"{prefix}{connector}{name}")


def print_directory_structure(paths, label=None):
    if label:
        print(label)
    if not paths:
        print("└── (none)\n")
        return

    tree = build_directory_tree(paths)
    _print_tree_node(tree)
    print()


print_directory_structure(added_files, label="ADDED")
print_directory_structure(modified_files, label="MODIFIED")
print_directory_structure(deleted_files, label="DELETED")
