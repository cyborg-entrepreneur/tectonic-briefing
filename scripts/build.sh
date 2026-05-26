#!/bin/bash
# ============================================================
# Tectonic Briefing — Build Pipeline
# Runs every step needed to bring the repo to a publishable state.
# Idempotent: safe to re-run any time.
#
# Pipeline (in order):
#   1. build-concept-pages.py
#        — parses STRUCTURAL_CONCEPTS.md
#        — finds pattern citations across all briefings
#        — generates concepts/<slug>.html for each pattern
#        — writes concepts/registry.json (canonical pattern data)
#        — writes search-index.json (briefings + concepts for cmd+K)
#
#   2. inject-vocab-badges.py
#        — strips existing vbadge wrappers (idempotent recovery)
#        — wraps pattern names in briefing prose with
#          <a class="vbadge mN" …> links to concept pages
#        — uses single-pass alternation regex (cannot corrupt
#          title attributes via cross-pattern contamination)
#
#   3. update-index.py
#        — regenerates index.html as a hero landing page with
#          today's briefing, vocabulary sparkline, archive
#        — idempotently injects per-day prev/next nav wrappers
#          into every briefing file
#
# Usage:
#   ./scripts/build.sh              # full build
#   ./scripts/build.sh --quiet      # suppress per-step output
#   ./scripts/build.sh --check      # build + report diff status only
# ============================================================

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

QUIET=0
CHECK_ONLY=0
for arg in "$@"; do
    case "$arg" in
        --quiet) QUIET=1 ;;
        --check) CHECK_ONLY=1 ;;
    esac
done

log() {
    if [[ $QUIET -eq 0 ]]; then
        echo "$@"
    fi
}

# Pre-flight: ensure python3 is available
if ! command -v python3 >/dev/null 2>&1; then
    echo "✗ python3 not found. Install Python 3 to run the build pipeline." >&2
    exit 1
fi

# Pre-flight: ensure required scripts exist
for script in build-concept-pages.py inject-vocab-badges.py update-index.py; do
    if [[ ! -f "scripts/$script" ]]; then
        echo "✗ Required script missing: scripts/$script" >&2
        exit 1
    fi
done

log "═══════════════════════════════════════════"
log "  Tectonic Briefing — Build Pipeline"
log "═══════════════════════════════════════════"
log ""

# ────────────────────────────────────────────────────────────
# Step 1 — Concept pages + registry + search index
# ────────────────────────────────────────────────────────────
log "[1/3] Generating concept pages + registry + search index…"
if [[ $QUIET -eq 1 ]]; then
    python3 scripts/build-concept-pages.py >/dev/null
else
    python3 scripts/build-concept-pages.py | sed 's/^/      /'
fi
log ""

# ────────────────────────────────────────────────────────────
# Step 2 — Inline vocabulary badges
# ────────────────────────────────────────────────────────────
log "[2/3] Injecting inline vocabulary badges into briefing prose…"
if [[ $QUIET -eq 1 ]]; then
    python3 scripts/inject-vocab-badges.py >/dev/null
else
    python3 scripts/inject-vocab-badges.py 2>&1 | tail -2 | sed 's/^/      /'
fi
log ""

# ────────────────────────────────────────────────────────────
# Step 3 — Index regen + per-day nav wrappers
# ────────────────────────────────────────────────────────────
log "[3/3] Regenerating index + per-day nav wrappers…"
if [[ $QUIET -eq 1 ]]; then
    python3 scripts/update-index.py >/dev/null
else
    python3 scripts/update-index.py 2>&1 | tail -3 | sed 's/^/      /'
fi
log ""

log "✓ Build complete"

# ────────────────────────────────────────────────────────────
# Optional: report diff status
# ────────────────────────────────────────────────────────────
if [[ $CHECK_ONLY -eq 1 ]]; then
    log ""
    log "─── Diff status ───"
    if [[ -n $(git status --porcelain 2>/dev/null) ]]; then
        log "  ⚠ Working tree has changes after build."
        git status --short | sed 's/^/      /'
        exit 1
    else
        log "  ✓ Working tree clean. No changes from build."
    fi
fi
