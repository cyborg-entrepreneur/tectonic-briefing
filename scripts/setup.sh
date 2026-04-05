#!/bin/bash
# ============================================================
# Tectonic Briefing — One-Time Setup
# Run this once to initialize the GitHub repo
# ============================================================

set -e

echo "═══════════════════════════════════════════"
echo "  Tectonic Briefing — Setup"
echo "═══════════════════════════════════════════"
echo ""

# Check if we're in the right place
REPO_DIR="$HOME/workflow/tectonic-briefing"

if [[ ! -d "$REPO_DIR" ]]; then
    echo "Creating directory: $REPO_DIR"
    mkdir -p "$REPO_DIR"
fi

cd "$REPO_DIR"

# Check if already a git repo
if [[ -d ".git" ]]; then
    echo "✓ Already a git repository"
else
    echo "Initializing git repository..."
    git init
    git branch -M main
fi

# Make scripts executable
chmod +x scripts/publish.sh 2>/dev/null || true
chmod +x scripts/new-briefing.sh 2>/dev/null || true

echo ""
echo "═══════════════════════════════════════════"
echo "  Next Steps (manual):"
echo "═══════════════════════════════════════════"
echo ""
echo "  1. Create a PRIVATE repo on GitHub:"
echo "     → https://github.com/new"
echo "     → Name: tectonic-briefing"
echo "     → Private: Yes"
echo "     → Don't initialize with README"
echo ""
echo "  2. Connect this repo to GitHub:"
echo "     git remote add origin git@github.com:YOUR_USERNAME/tectonic-briefing.git"
echo ""
echo "  3. Push the initial content:"
echo "     git add -A"
echo "     git commit -m 'Initial commit — Briefing No. 001'"
echo "     git push -u origin main"
echo ""
echo "  4. Enable GitHub Pages:"
echo "     → Repo Settings → Pages"
echo "     → Source: Deploy from a branch"
echo "     → Branch: main"
echo "     → Folder: / (root)"
echo "     → Save"
echo ""
echo "  5. Access your briefing at:"
echo "     https://YOUR_USERNAME.github.io/tectonic-briefing/"
echo ""
echo "  NOTE: Private repos require GitHub Pro for Pages."
echo "  Your .edu email (Virginia Tech) gives you GitHub Pro free."
echo "  Verify at: https://education.github.com/benefits"
echo ""
echo "═══════════════════════════════════════════"
echo "  Daily Workflow After Setup:"
echo "═══════════════════════════════════════════"
echo ""
echo "  1. Generate briefing in Claude conversation"
echo "  2. Download HTML → save to briefings/YYYY-MM-DD.html"
echo "  3. python3 scripts/update-index.py"
echo "  4. ./scripts/publish.sh"
echo ""
echo "═══════════════════════════════════════════"
