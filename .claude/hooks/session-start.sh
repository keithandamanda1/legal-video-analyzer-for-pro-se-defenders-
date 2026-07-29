#!/bin/bash
# Session-start hook — injects daily schedule + master checklist as context
# Claude reads this and delivers a prioritized daily briefing

SCHEDULE="$CLAUDE_PROJECT_DIR/DAILY_SCHEDULE.md"
CHECKLIST="$CLAUDE_PROJECT_DIR/DAILY_MASTER_CHECKLIST.md"

echo "=== KEITH'S DAILY LEGAL SCHEDULE — $(date '+%B %d, %Y') ==="
echo ""

if [ -f "$SCHEDULE" ]; then
  cat "$SCHEDULE"
else
  echo "No DAILY_SCHEDULE.md found — Claude will create one this session."
fi

echo ""
echo "--- FULL CASE REFERENCE ---"

if [ -f "$CHECKLIST" ]; then
  cat "$CHECKLIST"
else
  echo "No DAILY_MASTER_CHECKLIST.md found."
fi

echo ""
echo "=== END BRIEFING — Claude: read the above and deliver today's schedule to Keith ==="
echo "=== Check Gmail drafts for any unsent emails. Then give Keith his prioritized task list. ==="
