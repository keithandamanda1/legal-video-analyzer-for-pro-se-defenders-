#!/bin/bash
# Daily briefing hook — reads DAILY_STATUS.md and injects it as session context
# Claude will see this and brief the user on where they left off

STATUS_FILE="$CLAUDE_PROJECT_DIR/DAILY_STATUS.md"

if [ -f "$STATUS_FILE" ]; then
  echo "=== DAILY BRIEFING — Keith's Case Status ==="
  cat "$STATUS_FILE"
  echo "============================================="
else
  echo "=== No DAILY_STATUS.md found yet — Claude will create one at end of session ==="
fi
