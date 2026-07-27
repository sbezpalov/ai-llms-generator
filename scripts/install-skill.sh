#!/usr/bin/env bash
# Install all AIO suite skills into a project's .cursor/skills/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-.}"
SKILLS_ROOT="$TARGET/.cursor/skills"

# Refuse path escape attempts that look like absolute traversal jokes; still
# resolve to an absolute destination under the caller's chosen Target.
if [[ "$TARGET" == *".."* ]]; then
  echo "Refusing Target containing '..': $TARGET" >&2
  exit 1
fi

mkdir -p "$SKILLS_ROOT"

install_dir() {
  local name="$1"
  local src="$2"
  local dest="$SKILLS_ROOT/$name"
  mkdir -p "$dest"
  # Copy skill tree (files only one level + templates if present)
  cp -R "$src/." "$dest/"
  echo "Installed $name → $dest"
}

# generate-llms-txt lives at repo root (blog / zip BC)
GEN="$SKILLS_ROOT/generate-llms-txt"
mkdir -p "$GEN"
cp "$ROOT/SKILL.md" "$ROOT/PROMPT.md" "$ROOT/template-llms.txt" "$ROOT/example-llms.txt" "$GEN/"
echo "Installed generate-llms-txt → $GEN"

install_dir "audit-robots-ai-bots" "$ROOT/skills/audit-robots-ai-bots"
install_dir "draft-json-ld" "$ROOT/skills/draft-json-ld"
install_dir "aio-site-audit" "$ROOT/skills/aio-site-audit"

echo "AIO suite ready under $SKILLS_ROOT"
