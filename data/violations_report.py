#!/usr/bin/env python3
"""Export all case violations to a structured JSON/text report."""
import sys, json, datetime
sys.path.insert(0, '/home/user/legal-video-analyzer-for-pro-se-defenders-')
from database import get_db

db = get_db()

# Case info
case = db.execute('SELECT * FROM cases WHERE id=?',
    ('46f1b17b-8c69-48cf-a7bb-319d5db6f5f9',)).fetchone()
case_dict = dict(case)

# All violations with analysis info
cur = db.execute('''
    SELECT v.*, a.analysis_type, a.status as analysis_status
    FROM violations v
    JOIN analyses a ON v.analysis_id = a.id
    WHERE v.case_id = ?
    ORDER BY v.severity DESC, v.is_illegal DESC, v.is_red_flag DESC
''', ('46f1b17b-8c69-48cf-a7bb-319d5db6f5f9',))
violations = [dict(r) for r in cur.fetchall()]

report = {
    "generated_at": datetime.datetime.utcnow().isoformat(),
    "case": case_dict,
    "summary": {
        "total_violations": len(violations),
        "by_source": {},
        "severity_10": sum(1 for v in violations if v['severity'] == 10),
        "severity_9": sum(1 for v in violations if v['severity'] == 9),
        "is_illegal": sum(1 for v in violations if v['is_illegal']),
        "is_red_flag": sum(1 for v in violations if v['is_red_flag']),
    },
    "violations": violations,
}
for v in violations:
    src = v['analysis_type']
    report['summary']['by_source'][src] = report['summary']['by_source'].get(src, 0) + 1

with open('/home/user/legal-video-analyzer-for-pro-se-defenders-/data/exports/violations_full_report.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)
print(f"Exported {len(violations)} violations to violations_full_report.json")
print(json.dumps(report['summary'], indent=2, default=str))
