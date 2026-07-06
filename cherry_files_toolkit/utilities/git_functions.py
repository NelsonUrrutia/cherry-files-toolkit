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


def switch_branch(branch: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "checkout", branch], capture_output=True, text=True)

def checkout_files_from_branch(branch:str, files:list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "checkout", branch, '--'] + files, capture_output=True, text=True)

def stage_files(files: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "add"] + files, capture_output=True, text=True)

def commit(title: str, description:str = "") -> subprocess.CompletedProcess:
    cmd = ["git", "commit", "-m", title]
    if description.strip():
        cmd += ["-m", description]
    return subprocess.run(cmd, capture_output=True, text=True)

def cherry_pick_files(source_branch:str, target_branch:str, files:list[str], commit_title:str, commit_description: str = "") -> tuple[bool, str]:
    result = switch_branch(target_branch)
    if result.returncode != 0:
        return False, f"Failed to switch to {target_branch}: {result.stderr.strip()}"
    result = checkout_files_from_branch(source_branch, files)
    if result.returncode != 0:
        switch_branch(source_branch)
        return False, f"Failed to checkout files from {source_branch}: {result.stderr.strip()}"
    result = stage_files(files)
    if result.returncode != 0:
        switch_branch(source_branch)
        return False, f"Failed to stage files: {result.stderr.strip()}"
    result = commit(commit_title, commit_description)
    if result.returncode != 0:
        switch_branch(source_branch)
        return False, f"Failed to commit:{result.stderr.strip()}"
    switch_branch(source_branch)
    return True, "Cherry pick completed successfully"