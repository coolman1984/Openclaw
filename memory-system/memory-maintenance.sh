#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# Daily maintenance: validate, back up, and optionally push to git.
# Pass --push to commit and push to GitHub.

python3 memory-v3.py maintain --include-code "$@"
