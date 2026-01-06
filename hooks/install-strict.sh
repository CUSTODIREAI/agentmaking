#!/bin/bash
# Install STRICT Bender protection hook - blocks commits without changelog
# Usage: ./install-strict.sh /path/to/repo

REPO_PATH="${1:-.}"
SCRIPT_DIR="$(dirname "$0")"
HOOK_DEST="$REPO_PATH/.git/hooks/pre-commit"

if [ ! -d "$REPO_PATH/.git" ]; then
    echo "Error: $REPO_PATH is not a git repository"
    exit 1
fi

cp "$SCRIPT_DIR/pre-commit-strict" "$HOOK_DEST"
chmod +x "$HOOK_DEST"

echo "=============================================="
echo "  BENDER PROTECTION INSTALLED"
echo "=============================================="
echo ""
echo "Repository: $REPO_PATH"
echo ""
echo "Now ALL commits with .py/.sh/.yaml/.json changes"
echo "will REQUIRE a changelog entry."
echo ""
echo "Commits will be BLOCKED until you explain:"
echo "  - What changed"
echo "  - Why it changed"
echo ""
echo "View changelog: bender changelog"
echo "=============================================="
