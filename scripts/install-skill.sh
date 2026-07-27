#!/usr/bin/env bash
# Copy skill files into a target project's .cursor/skills/generate-llms-txt/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-.}"
DEST="$TARGET/.cursor/skills/generate-llms-txt"

mkdir -p "$DEST"
cp "$ROOT/SKILL.md" "$ROOT/PROMPT.md" "$ROOT/template-llms.txt" "$ROOT/example-llms.txt" "$DEST/"
echo "Installed generate-llms-txt → $DEST"
