#!/bin/bash
# Session-start hook — injects daily schedule + PCR checklist as context
# Claude reads this and delivers a prioritized daily briefing

SCHEDULE="$CLAUDE_PROJECT_DIR/DAILY_SCHEDULE.md"
CHECKLIST="$CLAUDE_PROJECT_DIR/DAILY_MASTER_CHECKLIST.md"

echo "=== KEITH'S DAILY PCR SCHEDULE — $(date '+%B %d, %Y') ==="
echo ""
echo "=== PROJECT BOUNDARY RULES — READ FIRST ==="
echo "THIS PROJECT IS FOR THE PCR CRIMINAL CASE ONLY: State v. Keith A. King, PENCD-CR-2018-03023"
echo ""
echo "If Keith mentions MHRC housing, Bangor Housing Authority, Brewer Housing Authority,"
echo "BHA, BrHA, BHA master key, housing revocation, or anything about his housing cases:"
echo "  → STOP. Tell Keith: 'That's the MHRC Housing project — we need to switch to that project.'"
echo "  → Do not continue working on that topic in this project."
echo ""
echo "If Keith mentions MRS, Maine Revenue Services, the tax levy, Case #1194093-S,"
echo "the $672 levy, or anything about the MRS case:"
echo "  → STOP. Tell Keith: 'That's the MRS Tax Levy project — we need to switch to that project.'"
echo "  → Do not continue working on that topic in this project."
echo ""
echo "Keith has ADHD and will sometimes drift to other cases mid-conversation."
echo "Your job is to catch it every time and gently redirect him."
echo "=== END BOUNDARY RULES ==="
echo ""

if [ -f "$SCHEDULE" ]; then
  cat "$SCHEDULE"
else
  echo "No DAILY_SCHEDULE.md found — Claude will create one this session."
fi

echo ""
echo "--- FULL PCR CASE REFERENCE ---"

if [ -f "$CHECKLIST" ]; then
  cat "$CHECKLIST"
else
  echo "No DAILY_MASTER_CHECKLIST.md found."
fi

echo ""
echo "=== END BRIEFING ==="
echo "Claude: Check Gmail drafts for any unsent emails. Then give Keith his prioritized PCR task list."
echo "If Keith drifts to MHRC housing or MRS levy topics, redirect him immediately."
