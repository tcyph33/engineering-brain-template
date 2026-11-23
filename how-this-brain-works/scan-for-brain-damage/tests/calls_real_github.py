"""calls_real_github: the mark on every test that calls the real GitHub, which gives the test
a connection, or skips it with the reason when the gh CLI can't be used."""

from __future__ import annotations

import functools
import unittest
from typing import Callable, Optional, TypeVar, cast

from github import GitHub

# The test case a marked test belongs to.
TestCaseType = TypeVar("TestCaseType", bound=unittest.TestCase)


def calls_real_github(
    test: Callable[[TestCaseType, GitHub], None]
) -> Callable[[TestCaseType], None]:
    """Marks a test as calling the real GitHub, and gives it a connection when it runs.

    Each run connects afresh, so no test shares a connection, or its cached answers, with
    another.

    Args:
        test: A test method that takes a GitHub connection after the test case.

    Returns:
        The test as unittest runs it: it connects, then runs, or skips when gh can't be used.
    """
    # Connect, skip when gh can't be used, and otherwise run the test with the connection
    @functools.wraps(test)
    def run_with_github(test_case: TestCaseType) -> None:
        """Runs the marked test with a fresh GitHub connection.

        Args:
            test_case: The test case running the test.

        Raises:
            unittest.SkipTest: If the gh CLI isn't installed or signed in.
        """
        # Skip without a connection
        SKIP_REASON: str = "calls the real GitHub, and the gh CLI isn't installed or signed in"
        github: Optional[GitHub] = GitHub.connect()
        is_connected: bool = (github is not None)
        if not is_connected:
            test_case.skipTest(SKIP_REASON)

        # Run the test with it
        test(test_case, cast(GitHub, github))

    # Hand unittest the connecting version, under the test's own name
    return run_with_github
