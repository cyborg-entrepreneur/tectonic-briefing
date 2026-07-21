#!/bin/bash
# ============================================================
# Tectonic Briefing — Publish Script
# One-command build + publish to GitHub Pages
# ============================================================
#
# Behavior:
#   1. Runs the build pipeline (build.sh) which regenerates
#      concept pages, injects vocabulary badges, refreshes
#      the index, and updates per-day nav wrappers.
#   2. Stages only the explicit public-site allowlist.
#   3. Commits with a passed-in message OR an auto-generated
#      "Briefing update — YYYY-MM-DD (N total)" message.
#   4. Pushes to origin.
#
# Usage:
#   ./scripts/publish.sh                         # auto commit message
#   ./scripts/publish.sh "Briefing No. 047 — …"  # custom message
#   ./scripts/publish.sh --build-only            # build, no git
#   ./scripts/publish.sh --dry-run               # build + show what would commit
# ============================================================

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

BUILD_ONLY=0
DRY_RUN=0
CUSTOM_MSG=""
for arg in "$@"; do
    case "$arg" in
        --build-only) BUILD_ONLY=1 ;;
        --dry-run) DRY_RUN=1 ;;
        --*) echo "Unknown flag: $arg"; exit 2 ;;
        *) CUSTOM_MSG="$arg" ;;
    esac
done

# ────────────────────────────────────────────────────────────
# Step 0 — Run the build pipeline
# ────────────────────────────────────────────────────────────
"$REPO_DIR/scripts/build.sh"
echo ""

if [[ $BUILD_ONLY -eq 1 ]]; then
    echo "✓ Build complete (--build-only specified; no git operations)."
    exit 0
fi

# ────────────────────────────────────────────────────────────
# Step 1 — Detect changes
# ────────────────────────────────────────────────────────────
if [[ -z $(git status --porcelain) ]]; then
    echo "✓ No changes to publish."
    exit 0
fi

# Count briefings + identify latest for the commit message
BRIEFING_COUNT=$(ls -1 briefings/*.html 2>/dev/null | wc -l | tr -d ' ')
LATEST_PATH=$(ls -1 briefings/*.html 2>/dev/null | sort -r | sed -n '1p')
LATEST=$(basename "$LATEST_PATH" .html)

echo "═══════════════════════════════════════════"
echo "  Tectonic Briefing — Publishing"
echo "═══════════════════════════════════════════"
echo ""
echo "  Briefings in archive: $BRIEFING_COUNT"
echo "  Latest briefing:      $LATEST"

# Show diff stat
echo ""
echo "  Pending changes:"
git status --short | sed 's/^/    /' | head -20
TOTAL_CHANGED=$(git status --porcelain | wc -l | tr -d ' ')
if [[ $TOTAL_CHANGED -gt 20 ]]; then
    echo "    … and $(( TOTAL_CHANGED - 20 )) more"
fi
echo ""

# ────────────────────────────────────────────────────────────
# Step 2 — Stage + commit
# ────────────────────────────────────────────────────────────
if [[ -n "$CUSTOM_MSG" ]]; then
    COMMIT_MSG="$CUSTOM_MSG"
else
    TODAY=$(date +"%Y-%m-%d")
    COMMIT_MSG="Briefing update — $TODAY ($BRIEFING_COUNT total)"
fi

if [[ $DRY_RUN -eq 1 ]]; then
    echo "[dry-run] Would commit with message:"
    echo "    $COMMIT_MSG"
    echo "[dry-run] Would push to origin."
    echo ""
    echo "✓ Dry run complete. Nothing committed or pushed."
    exit 0
fi

STAGE_PATHS=(
    briefings concepts scripts index.html search-index.json
    STRUCTURAL_CONCEPTS.md README.md CLAUDE.md CONTINGENCY_AUDIT.md .gitignore
)
for optional_path in articles synthesis assets threads; do
    # Skip if missing, or if gitignored (git add would exit 1 under set -e
    # and silently abort the script mid-run). articles/ is deliberately
    # gitignored — its content ships via the cyborg-entrepreneurship site.
    if [[ -e "$optional_path" ]] && ! git check-ignore -q "$optional_path"; then
        STAGE_PATHS+=("$optional_path")
    fi
done
git add -- "${STAGE_PATHS[@]}"

# Do not silently sweep unrelated local work into a public-site commit.
if ! git diff --quiet; then
    echo "✗ Unstaged tracked changes remain outside the publish allowlist:" >&2
    git diff --name-only | sed 's/^/    /' >&2
    exit 1
fi
UNTRACKED=$(git ls-files --others --exclude-standard)
if [[ -n "$UNTRACKED" ]]; then
    echo "✗ Untracked files remain outside the publish allowlist:" >&2
    echo "$UNTRACKED" | sed 's/^/    /' >&2
    exit 1
fi
if git diff --cached --quiet; then
    echo "✓ No allowlisted changes to publish."
    exit 0
fi
git commit -m "$COMMIT_MSG"

# ────────────────────────────────────────────────────────────
# Step 3 — Push to origin
# ────────────────────────────────────────────────────────────
git push

echo ""
echo "═══════════════════════════════════════════"
echo "  ✓ Published successfully"
PAGES_URL=$(git remote get-url origin 2>/dev/null | sed 's/.*github.com[:/]//' | sed 's/.git$//' | sed 's/\(.*\)\/\(.*\)/\1.github.io\/\2/')
if [[ -n "$PAGES_URL" ]]; then
    echo "  View at: https://$PAGES_URL/"
fi
echo "═══════════════════════════════════════════"
