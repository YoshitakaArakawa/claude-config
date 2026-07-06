#!/usr/bin/env bash
# init_fable_workspace.sh — scaffold the Fable-mode working files for a
# Deep-mode task from assets/templates/. Usage: init_fable_workspace.sh [dir]
# Idempotent: never overwrites existing files.
# No bash available? The same templates live in assets/templates/ — copy
# them with file tools instead.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TPL="$SCRIPT_DIR/../assets/templates"
DIR="${1:-.}/fable-workspace"
mkdir -p "$DIR/memory/lessons"

copy_if_absent() {
  local src="$1" dst="$2"
  if [ -e "$dst" ]; then
    echo "skip (exists): $dst"
  else
    cp "$src" "$dst"
    echo "created: $dst"
  fi
}

copy_if_absent "$TPL/PLAN.md"                 "$DIR/PLAN.md"
copy_if_absent "$TPL/implementation-notes.md" "$DIR/implementation-notes.md"
copy_if_absent "$TPL/VERIFICATION.md"         "$DIR/VERIFICATION.md"
copy_if_absent "$TPL/memory-README.md"        "$DIR/memory/README.md"

echo "Fable workspace ready at: $DIR"
echo "On-demand templates (use when needed, not copied):"
echo "  $TPL/verifier-prompt.md   (fresh-context verifier subagent)"
echo "  $TPL/pr-description.md    (human/agent change description)"
