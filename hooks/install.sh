#!/bin/bash
# Install Bender git hooks in a repository
# Usage: ./install.sh /path/to/repo

REPO_PATH="${1:-.}"
HOOK_SOURCE="$(dirname "$0")/post-commit"
HOOK_DEST="$REPO_PATH/.git/hooks/post-commit"

if [ ! -d "$REPO_PATH/.git" ]; then
    echo "Error: $REPO_PATH is not a git repository"
    exit 1
fi

cp "$HOOK_SOURCE" "$HOOK_DEST"
chmod +x "$HOOK_DEST"

echo "Bender hook installed in $REPO_PATH"
echo ""
echo "Now when you commit changes to .py or .sh files,"
echo "Bender will ask for a changelog entry!"
