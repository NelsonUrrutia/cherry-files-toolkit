#!/usr/bin/env bash
# Show all files created, modified, or deleted on a branch relative to a base branch.
# Usage: cherry-files-diff [branch-name] [--base <base-branch>] [--tree] [--no-color] [--help]

set -euo pipefail

# ── Help ───────────────────────────────────────────────────────────────────────
for arg in "$@"; do
  if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
    cat <<'EOF'
cherry-files-diff — Show all files changed on a branch, grouped by folder.

USAGE
  cherry-files-diff [branch] [--base <base-branch>] [--tree] [--no-color] [--help]

ARGUMENTS
  branch              Branch to inspect. Defaults to the current branch.

FLAGS
  --base <branch>     Branch to compare against. Defaults to "main".
  --tree              Output as a file tree (ideal for saving to a file).
  --no-color          Disable color output (also auto-disabled when piping).
  -h, --help          Show this help message.

EXAMPLES
  cherry-files-diff
      Compare the current branch against main.

  cherry-files-diff my-feature --base develop
      Compare my-feature against develop.

  cherry-files-diff --tree > changes.txt
      Save a tree-formatted plain-text report to a file.

OUTPUT
  Files are grouped by top-level folder and categorized as:
    +  CREATED   — files added on the branch
    ~  MODIFIED  — files changed on the branch
    -  DELETED   — files removed on the branch
EOF
    exit 0
  fi
done

# ── Color support ──────────────────────────────────────────────────────────────
USE_COLOR=true
for arg in "$@"; do
  [[ "$arg" == "--no-color" ]] && USE_COLOR=false
done
[[ "${NO_COLOR:-}" != "" ]] && USE_COLOR=false
[ -t 1 ] || USE_COLOR=false
if $USE_COLOR && ! tput colors &>/dev/null 2>&1; then
  USE_COLOR=false
fi

if $USE_COLOR; then
  GREEN="\033[0;32m"
  YELLOW="\033[0;33m"
  RED="\033[0;31m"
  BOLD="\033[1m"
  DIM="\033[2m"
  RESET="\033[0m"
else
  GREEN="" YELLOW="" RED="" BOLD="" DIM="" RESET=""
fi

err() { printf "${RED}ERROR:${RESET} %s\n" "$*" >&2; }

# ── Guard: must be inside a git repo ──────────────────────────────────────────
if ! git rev-parse --git-dir &>/dev/null; then
  err "Not inside a git repository."
  exit 1
fi

# ── Parse arguments ───────────────────────────────────────────────────────────
BRANCH=""
BASE="main"
TREE=false
skip_next=false

for arg in "$@"; do
  if $skip_next; then
    BASE="$arg"
    skip_next=false
    continue
  fi
  case "$arg" in
  --no-color | --help | -h) ;;
  --tree) TREE=true ;;
  --base) skip_next=true ;;
  *) [[ -z "$BRANCH" ]] && BRANCH="$arg" ;;
  esac
done

if [[ -z "$BRANCH" ]]; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD)
  printf "${DIM}No branch specified. Using current branch: %s${RESET}\n" "$BRANCH"
fi

# ── Guard: branches must exist ────────────────────────────────────────────────
branch_exists() {
  git show-ref --verify --quiet "refs/heads/$1" ||
    git show-ref --verify --quiet "refs/remotes/origin/$1"
}

if ! branch_exists "$BRANCH"; then
  err "Branch '$BRANCH' not found locally or on origin."
  echo ""
  echo "Available local branches:"
  git branch --list | sed 's/^/  /'
  exit 1
fi

if ! branch_exists "$BASE"; then
  err "Base branch '$BASE' not found locally or on origin."
  echo ""
  echo "Available local branches:"
  git branch --list | sed 's/^/  /'
  exit 1
fi

# ── Guard: branch and base must differ ────────────────────────────────────────
if [[ "$BRANCH" == "$BASE" ]]; then
  err "Branch and base are both '$BRANCH'. Select a different branch to compare."
  exit 1
fi

# ── Find divergence point ─────────────────────────────────────────────────────
MERGE_BASE=$(git merge-base "$BASE" "$BRANCH" 2>/dev/null) || {
  err "Could not compute merge-base between '$BASE' and '$BRANCH'."
  exit 1
}
MERGE_BASE_SHORT="${MERGE_BASE:0:8}"

echo ""
printf "${BOLD}Branch diff: %s${RESET}\n" "$BRANCH"
printf "${DIM}Comparing from merge-base %s (where %s diverged from %s)${RESET}\n" "$MERGE_BASE_SHORT" "$BRANCH" "$BASE"
echo ""

# ── Get all changed files ─────────────────────────────────────────────────────
DIFF_OUTPUT=$(git diff --name-status "$MERGE_BASE".."$BRANCH" 2>/dev/null)

if [[ -z "$DIFF_OUTPUT" ]]; then
  printf "${DIM}No file changes found between '%s' and '%s'.${RESET}\n" "$BASE" "$BRANCH"
  exit 0
fi

# ── Parse into buckets ────────────────────────────────────────────────────────
ADDED=$(echo "$DIFF_OUTPUT" | awk '$1 == "A" {print $2}')
MODIFIED=$(echo "$DIFF_OUTPUT" | awk '$1 == "M" {print $2}')
DELETED=$(echo "$DIFF_OUTPUT" | awk '$1 == "D" {print $2}')

count() { [[ -z "$1" ]] && echo 0 || echo "$1" | grep -c .; }
COUNT_A=$(count "$ADDED")
COUNT_M=$(count "$MODIFIED")
COUNT_D=$(count "$DELETED")
COUNT_TOTAL=$((COUNT_A + COUNT_M + COUNT_D))

# ── Summary header ────────────────────────────────────────────────────────────
printf "${BOLD}Summary:${RESET}  "
printf "${GREEN}+%d created${RESET}  " "$COUNT_A"
printf "${YELLOW}~%d modified${RESET}  " "$COUNT_M"
printf "${RED}%s deleted${RESET}\n" "-${COUNT_D}"
echo ""

# ── Tree output ───────────────────────────────────────────────────────────────
print_as_tree() {
  local files="$1" label="$2" cat_conn="$3" cat_pipe="$4"

  printf "%s %s\n" "$cat_conn" "$label"

  local folder_arr=()
  while IFS= read -r line; do
    folder_arr+=("$line")
  done < <(echo "$files" | awk -F'/' 'NF > 1 {print $1} NF == 1 {print "(root)"}' | sort -u)

  local nfolders=${#folder_arr[@]}
  local fi
  for ((fi = 0; fi < nfolders; fi++)); do
    local folder="${folder_arr[$fi]}"
    local folder_conn="├──" folder_pipe="│   "
    if [[ $fi -eq $((nfolders - 1)) ]]; then
      folder_conn="└──"
      folder_pipe="    "
    fi

    local folder_files
    if [[ "$folder" == "(root)" ]]; then
      folder_files=$(echo "$files" | awk -F'/' 'NF == 1')
    else
      folder_files=$(echo "$files" | awk -v f="$folder/" 'index($0, f) == 1 {print substr($0, length(f)+1)}')
    fi

    local file_arr=()
    while IFS= read -r line; do
      file_arr+=("$line")
    done <<<"$folder_files"

    local nfiles=${#file_arr[@]}
    printf "%s %s %s/ (%d)\n" "$cat_pipe" "$folder_conn" "$folder" "$nfiles"

    local fj
    for ((fj = 0; fj < nfiles; fj++)); do
      local file_conn="├──"
      if [[ $fj -eq $((nfiles - 1)) ]]; then file_conn="└──"; fi
      printf "%s %s %s %s\n" "$cat_pipe" "$folder_pipe" "$file_conn" "${file_arr[$fj]}"
    done
  done
}

# ── Grouped output ────────────────────────────────────────────────────────────
print_by_folder() {
  local files="$1" prefix="$2" color="$3"

  local folders
  folders=$(echo "$files" | awk -F'/' 'NF > 1 {print $1} NF == 1 {print "(root)"}' | sort -u)

  while IFS= read -r folder; do
    local folder_files folder_count
    if [[ "$folder" == "(root)" ]]; then
      folder_files=$(echo "$files" | awk -F'/' 'NF == 1')
    else
      folder_files=$(echo "$files" | awk -v f="$folder/" 'index($0, f) == 1 {print substr($0, length(f)+1)}')
    fi
    folder_count=$(echo "$folder_files" | grep -c .)
    printf "  ${BOLD}%s/${RESET} ${DIM}(%d)${RESET}\n" "$folder" "$folder_count"
    echo "$folder_files" | while IFS= read -r fname; do
      printf "    ${color}%s${RESET} %s\n" "$prefix" "$fname"
    done
  done <<<"$folders"
  echo ""
}

if $TREE; then
  printf "%s (vs %s)\n" "$BRANCH" "$BASE"

  cat_arr=()
  if [[ $COUNT_A -gt 0 ]]; then cat_arr+=("A"); fi
  if [[ $COUNT_M -gt 0 ]]; then cat_arr+=("M"); fi
  if [[ $COUNT_D -gt 0 ]]; then cat_arr+=("D"); fi

  ncats=${#cat_arr[@]}
  for ((ci = 0; ci < ncats; ci++)); do
    cat_conn="├──"
    cat_pipe="│  "
    if [[ $ci -eq $((ncats - 1)) ]]; then
      cat_conn="└──"
      cat_pipe="   "
    fi
    case "${cat_arr[$ci]}" in
    A) print_as_tree "$ADDED" "CREATED ($COUNT_A)" "$cat_conn" "$cat_pipe" ;;
    M) print_as_tree "$MODIFIED" "MODIFIED ($COUNT_M)" "$cat_conn" "$cat_pipe" ;;
    D) print_as_tree "$DELETED" "DELETED ($COUNT_D)" "$cat_conn" "$cat_pipe" ;;
    esac
  done
  echo ""
else
  if [[ $COUNT_A -gt 0 ]]; then
    printf "${GREEN}${BOLD}CREATED (%d)${RESET}\n" "$COUNT_A"
    print_by_folder "$ADDED" "+" "$GREEN"
  fi
  if [[ $COUNT_M -gt 0 ]]; then
    printf "${YELLOW}${BOLD}MODIFIED (%d)${RESET}\n" "$COUNT_M"
    print_by_folder "$MODIFIED" "~" "$YELLOW"
  fi
  if [[ $COUNT_D -gt 0 ]]; then
    printf "${RED}${BOLD}DELETED (%d)${RESET}\n" "$COUNT_D"
    print_by_folder "$DELETED" "-" "$RED"
  fi
fi

# ── Footer ────────────────────────────────────────────────────────────────────
printf "${BOLD}Total: %d files touched on '%s'${RESET}\n" "$COUNT_TOTAL" "$BRANCH"
printf "${DIM}(merge-base: %s)${RESET}\n" "$MERGE_BASE_SHORT"
echo ""