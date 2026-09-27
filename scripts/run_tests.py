#!/usr/bin/env python3
"""Run stdlib tests and preserve an explicit result record; no network required."""
import io
import json
from pathlib import Path
import platform
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
print(stream.getvalue())
record={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
        'successful':result.wasSuccessful(),'python':platform.python_version(),'platform':platform.system(),
        'scope':'Local automated tests of this release, not upstream repository tests or clinical validation.'}
(ROOT/'validation').mkdir(exist_ok=True)
(ROOT/'validation/test_results.json').write_text(json.dumps(record,indent=2)+'\n')
(ROOT/'validation/test_log.txt').write_text(stream.getvalue())
raise SystemExit(0 if result.wasSuccessful() else 1)
