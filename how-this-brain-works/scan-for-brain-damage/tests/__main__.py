"""Run the brain scan's tests.

Usage, from the brain's root:
    python3 how-this-brain-works/scan-for-brain-damage/tests

This is the way to run them: it puts the scan's folder on the import path, as running the
scan does, so tests import its modules by name. Exit status: 0 when every test passes, 1
otherwise. Each test builds its brain in a temporary folder that's removed when the test
ends, whether it passed or failed, and no bytecode is written, so a run leaves nothing
behind. Tests marked @calls_real_github are skipped, with the reason, when the gh CLI can't
be used.
"""

from __future__ import annotations

import sys

# Write no __pycache__ folders; this has to run before anything else is imported
sys.dont_write_bytecode = True

import unittest  # noqa: E402 - imported after turning off bytecode on purpose
from pathlib import Path  # noqa: E402


def main() -> int:
    """Finds and runs every test in this folder.

    Returns:
        The process exit status: 0 when every test passes, 1 otherwise.
    """
    # Let tests import the scan's modules by name, as the scan's own modules do
    tests_folder: Path = Path(__file__).resolve().parent
    scan_folder: Path = tests_folder.parent
    sys.path.insert(0, str(scan_folder))

    # Run every test_*.py file in this folder
    suite: unittest.TestSuite = unittest.defaultTestLoader.discover(
        start_dir=str(tests_folder), top_level_dir=str(tests_folder)
    )
    result: unittest.TestResult = unittest.TextTestRunner().run(suite)

    # Say why tests were skipped, since the summary only counts them
    skip_reasons: list[str] = []
    skipped_test: unittest.TestCase
    skip_reason: str
    for skipped_test, skip_reason in result.skipped:
        skip_reasons.append(skip_reason)
    distinct_reason: str
    for distinct_reason in sorted(set(skip_reasons)):
        print(f"Skipped {skip_reasons.count(distinct_reason)}: {distinct_reason}")

    # Exit 1 when anything failed
    ALL_PASSED_STATUS: int = 0
    FAILED_STATUS: int = 1
    is_passing: bool = (result.wasSuccessful())
    exit_status: int = ALL_PASSED_STATUS if is_passing else FAILED_STATUS
    return exit_status


# Run the tests when executed
is_run_as_script: bool = (__name__ == "__main__")
if is_run_as_script:
    sys.exit(main())
