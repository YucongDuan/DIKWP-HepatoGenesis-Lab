#!/usr/bin/env python3
"""Isolated reproduction of one inspected scoring expression, not upstream tests."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hepatogenesis.common import Invalid,number,write_json
score=max(0,min(100,float('nan')-0-0))
rejected=False
try:number(float('nan'),'quality')
except Invalid:rejected=True
record={'scope':'Isolated expression reproduction from the inspected V2 closure path; no full upstream repository execution.',
        'upstream_repository':'YucongDuan/DIKWP-HepatoScholar-Studio-V2',
        'git_blob_sha':'c67252ea3f4ad8f686137b4b2ed2907841c33275',
        'expression':'max(0, min(100, float("nan") - 0 - 0))',
        'observed_score':score,'corresponding_inspected_threshold_level':'S4' if score>=85 else 'other',
        'new_finite_validator_rejected_input':rejected}
write_json(Path(__file__).resolve().parents[1]/'validation/upstream_edge_reproduction.json',record)
print(record)
if score!=100 or not rejected:raise SystemExit(1)
