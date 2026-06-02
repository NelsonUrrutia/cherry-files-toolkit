import subprocess

def is_git_repo() -> bool:
    result = subprocess.run(["git","rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
    if result.stdout.strip() == "true":
        return True 
    else: 
        return False 

def get_current_branch() -> str:
    result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
    return result.stdout.strip()

def get_branches() -> list[str]:
    "Returns an array with the repository branches"
    if not is_git_repo():
        return []

    result = subprocess.run(["git", "branch", "-l"], capture_output=True, text=True)
    branches = [line.replace("*","").strip() for line in result.stdout.splitlines()]
    return branches

def get_divergence_point(base:str, branch:str) -> str:
    result = subprocess.run(["git", "merge-base", base, branch], capture_output=True, text=True)
    commit_id = result.stdout.strip()
    commit_id = commit_id[:8]
    return commit_id

def get_all_changed_files(divergent:str, commit_id:str) -> list[str]:
    result = subprocess.run(["git", "diff", "--name-status", f"{commit_id}..{divergent}"], capture_output=True, text=True)
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return lines
