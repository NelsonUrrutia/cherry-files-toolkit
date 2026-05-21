import subprocess

def is_git_repo() -> bool:
    result = subprocess.run(["git","rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
    if result.stdout.strip() == "true":
        return True 
    else: 
        return False 

def get_branches() -> list[str]:
    "Returns an array with the repository branches"
    if not is_git_repo():
        return []

    result = subprocess.run(["git", "branch", "-l"], capture_output=True, text=True)
    branches = [line.replace("*","").strip() for line in result.stdout.splitlines()]
    return branches


