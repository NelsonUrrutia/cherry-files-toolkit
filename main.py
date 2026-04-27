import subprocess
import sys

# Guard must be inside a git repo
git_dir_process = subprocess.run(
    ["git", "rev-parse", "--git-dir"], capture_output=True, text=True
)
git_dir_process_return_code = git_dir_process.returncode

if git_dir_process_return_code != 0:
    print("Not inside a git repository")
    sys.exit()
