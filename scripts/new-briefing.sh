#!/bin/bash
# ============================================================
# Tectonic Briefing — New Briefing Scaffold
# Creates a dated HTML file ready for content from Claude
# Usage: ./scripts/new-briefing.sh [YYYY-MM-DD]
# ============================================================

set -e

REPO_DIR="$HOME/workflow/tectonic-briefing"
cd "$REPO_DIR"

# Date defaults to today
DATE="${1:-$(date +%Y-%m-%d)}"
FILENAME="briefings/${DATE}.html"

if [[ -f "$FILENAME" ]]; then
    echo "⚠  Briefing already exists: $FILENAME"
    echo "   Edit it directly or delete and re-run."
    exit 1
fi

# Count existing briefings for numbering
BRIEFING_COUNT=$(ls -1 briefings/*.html 2>/dev/null | wc -l | tr -d ' ')
NEXT_NUM=$(printf "%03d" $((BRIEFING_COUNT + 1)))

# Format display date
DISPLAY_DATE=$(date -j -f "%Y-%m-%d" "$DATE" "+%e %B %Y" 2>/dev/null || date -d "$DATE" "+%e %B %Y" 2>/dev/null || echo "$DATE")

echo "═══════════════════════════════════════════"
echo "  Creating Briefing No. $NEXT_NUM"
echo "  Date: $DISPLAY_DATE"
echo "  File: $FILENAME"
echo "═══════════════════════════════════════════"

cat > "$FILENAME" << TEMPLATE
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tectonic Briefing — ${DISPLAY_DATE}</title>
<!-- PASTE FULL BRIEFING HTML FROM CLAUDE CONVERSATION HERE -->
<!-- Replace this entire file content with the generated briefing -->
</head>
<body>
<p>Briefing No. ${NEXT_NUM} — ${DISPLAY_DATE}</p>
<p>Replace this file with the briefing generated in Claude conversation.</p>
</body>
</html>
TEMPLATE

echo ""
echo "✓ Scaffold created: $FILENAME"
echo ""
echo "Next steps:"
echo "  1. Generate briefing in Claude conversation"
echo "  2. Download the HTML file from Claude"
echo "  3. Replace $FILENAME with the downloaded file"
echo "     OR copy content: pbpaste > $FILENAME"
echo "  4. Update index.html with new entry"
echo "  5. Run ./scripts/publish.sh"
