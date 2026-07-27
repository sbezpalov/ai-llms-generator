#!/usr/bin/env bash
# Install all AIO suite skills into a project's .cursor/skills/.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: install-skill.sh [--dry-run] [--force] [TARGET]

TARGET must be an existing project directory (default: current directory).
The installer refuses to overwrite an existing skill by default.

Options:
  --dry-run  Show planned actions without writing files.
  --force    Back up existing skill directories, then install clean copies.
  -h, --help Show this help.
EOF
}

FORCE=false
DRY_RUN=false
TARGET=""

while (($# > 0)); do
  case "$1" in
    --force)
      FORCE=true
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [[ -n "$TARGET" ]]; then
        echo "Only one TARGET may be provided." >&2
        exit 2
      fi
      TARGET="$1"
      ;;
  esac
  shift
done

TARGET="${TARGET:-.}"
if [[ ! -d "$TARGET" ]]; then
  echo "TARGET must be an existing directory: $TARGET" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
TARGET_ABS="$(cd "$TARGET" && pwd -P)"
SKILLS_ROOT="$TARGET_ABS/.cursor/skills"
BACKUP_SUFFIX=".backup-$(date -u +%Y%m%dT%H%M%SZ)"
SKILL_NAMES=(
  "generate-llms-txt"
  "audit-robots-ai-bots"
  "draft-json-ld"
  "aio-site-audit"
)

# Preflight every destination before making any change.
for name in "${SKILL_NAMES[@]}"; do
  dest="$SKILLS_ROOT/$name"
  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ "$FORCE" != true ]]; then
      echo "Refusing to overwrite existing skill: $dest" >&2
      echo "Re-run with --force to create a backup and install a clean copy." >&2
      exit 1
    fi
    backup="$dest$BACKUP_SUFFIX"
    if [[ -e "$backup" || -L "$backup" ]]; then
      echo "Backup destination already exists: $backup" >&2
      exit 1
    fi
  fi
done

if [[ "$DRY_RUN" == true ]]; then
  for name in "${SKILL_NAMES[@]}"; do
    dest="$SKILLS_ROOT/$name"
    if [[ -e "$dest" || -L "$dest" ]]; then
      echo "Would back up $dest → $dest$BACKUP_SUFFIX"
    fi
    echo "Would install $name → $dest"
  done
  exit 0
fi

mkdir -p "$SKILLS_ROOT"

prepare_dest() {
  local dest="$1"
  if [[ -e "$dest" || -L "$dest" ]]; then
    mv "$dest" "$dest$BACKUP_SUFFIX"
    echo "Backed up $dest → $dest$BACKUP_SUFFIX"
  fi
  mkdir -p "$dest"
}

install_dir() {
  local name="$1"
  local src="$2"
  local dest="$SKILLS_ROOT/$name"
  prepare_dest "$dest"
  cp -R "$src/." "$dest/"
  echo "Installed $name → $dest"
}

# generate-llms-txt lives at repo root for blog/zip backwards compatibility.
GEN="$SKILLS_ROOT/generate-llms-txt"
prepare_dest "$GEN"
cp \
  "$ROOT/SKILL.md" \
  "$ROOT/PROMPT.md" \
  "$ROOT/PROMPT.en.md" \
  "$ROOT/template-llms.txt" \
  "$ROOT/example-llms.txt" \
  "$GEN/"
echo "Installed generate-llms-txt → $GEN"

install_dir "audit-robots-ai-bots" "$ROOT/skills/audit-robots-ai-bots"
install_dir "draft-json-ld" "$ROOT/skills/draft-json-ld"
install_dir "aio-site-audit" "$ROOT/skills/aio-site-audit"

echo "AIO suite ready under $SKILLS_ROOT"
