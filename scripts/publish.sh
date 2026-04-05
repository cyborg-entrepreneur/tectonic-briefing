#!/bin/bash
# ============================================================
# Tectonic Briefing — Publish Script
# One-command publish to GitHub Pages
# ============================================================

set -e

REPO_DIR="$HOME/workflow/tectonic-briefing"
cd "$REPO_DIR"

# Check for uncommitted changes
if [[ -z $(git status --porcelain) ]]; then
    echo "✓ No changes to publish."
    exit 0
fi

# Count briefings for commit message
BRIEFING_COUNT=$(ls -1 briefings/*.html 2>/dev/null | wc -l | tr -d ' ')
LATEST=$(ls -1 briefings/*.html 2>/dev/null | sort -r | head -1 | xargs basename .html 2>/dev/null)

echo "═══════════════════════════════════════════"
echo "  Tectonic Briefing — Publishing"
echo "═══════════════════════════════════════════"
echo ""
echo "  Briefings in archive: $BRIEFING_COUNT"
echo "  Latest briefing:      $LATEST"
echo ""

# Stage all changes
git add -A

# Generate commit message
if [[ -n "$1" ]]; then
    # Custom message provided
    COMMIT_MSG="$1"
else
    # Auto-generate
    TODAY=$(date +"%Y-%m-%d")
    COMMIT_MSG="Briefing update — $TODAY ($BRIEFING_COUNT total)"
fi

git commit -m "$COMMIT_MSG"
git push

echo ""
echo "═══════════════════════════════════════════"
echo "  ✓ Published successfully"
echo "  View at: https://$(git remote get-url origin | sed 's/.*github.com[:/]//' | sed 's/.git$//' | sed 's/\(.*\)\/\(.*\)/\1.github.io\/\2/')/"
echo "═══════════════════════════════════════════"
