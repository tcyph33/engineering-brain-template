"""Scan this brain for damage: notes that break the manual's rules, links that lead nowhere,
and pointers that no longer hold.

Usage, from the brain's root:
    python3 how-this-brain-works/scan-for-brain-damage [--skip-pointers]

Exit status: 0 when nothing must be fixed, 1 when the scan found errors, 2 when the brain
couldn't be read. The rules it checks are the ones in how-this-brain-works/README.md; when a
rule there changes, its check here changes with it.

Python puts this folder on the import path when it runs it, which is how the modules here
import each other by name.
"""

from __future__ import annotations

import sys

# Stop with a clear message on Python older than 3.9, whose syntax the scan's modules use;
# this has to run before they're imported
MINIMUM_PYTHON_VERSION: tuple[int, int] = (3, 9)
is_python_too_old: bool = (sys.version_info[:2] < MINIMUM_PYTHON_VERSION)
if is_python_too_old:
    sys.exit("The brain scan needs Python 3.9 or later.")

import argparse  # noqa: E402 - imported after the version check on purpose
from pathlib import Path  # noqa: E402
from typing import Optional, cast  # noqa: E402

from brain import Brain, BrainLoadError  # noqa: E402
from checks.pointer_damage import find_pointer_damage  # noqa: E402
from damage import Damage, Severity  # noqa: E402
from damage_report import print_damage_report  # noqa: E402
from github import GitHub  # noqa: E402
from scan_for_brain_damage import scan_for_brain_damage  # noqa: E402

# The option that leaves the GitHub pointer checks out.
SKIP_POINTERS_OPTION: str = "--skip-pointers"


def main() -> int:
    """Runs the scan from the command line: loads the brain, scans it, and reports.

    Returns:
        The process exit status: 0 when nothing must be fixed, 1 when errors were found,
        2 when the brain couldn't be read.

    Raises:
        SystemExit: If the command-line options are invalid, or --help was asked for.
    """
    # Read the options
    options: argparse.Namespace = _parse_options()

    # Load the brain this scan lives in, stopping if it can't be read
    try:
        brain: Brain = Brain.load(_brain_root())
    except BrainLoadError as error:
        UNREADABLE_BRAIN_STATUS: int = 2
        _print_load_failure(error)
        return UNREADABLE_BRAIN_STATUS

    # Scan its files, and its pointers unless asked not to
    damage: list[Damage] = scan_for_brain_damage(brain)
    should_check_pointers: bool = (not options.skip_pointers)
    if should_check_pointers:
        damage.extend(_check_pointers(brain))

    # Report what was found, and set the exit status from it
    print_damage_report(damage)
    exit_status: int = _exit_status(damage)
    return exit_status


def _check_pointers(brain: Brain) -> list[Damage]:
    """Checks the brain's pointers against GitHub, or warns when GitHub can't be reached.

    Args:
        brain: The brain to scan.

    Returns:
        The pointer damage found, or one warning saying the checks didn't run.
    """
    # Warn instead of checking when gh isn't installed or signed in
    github: Optional[GitHub] = GitHub.connect()
    is_connected: bool = (github is not None)
    if not is_connected:
        unconnected_damage: list[Damage] = [Damage(
            Severity.WARNING,
            "pointers",
            "not checked: the gh CLI isn't installed or signed in (run 'gh auth login'), "
            f"or pass {SKIP_POINTERS_OPTION}",
        )]
        return unconnected_damage
    pointer_damage: list[Damage] = find_pointer_damage(brain, cast(GitHub, github))
    return pointer_damage


def _exit_status(damage: list[Damage]) -> int:
    """The exit status for what the scan found.

    Args:
        damage: Everything the scan found.

    Returns:
        1 when there are errors, 0 otherwise.
    """
    # Exit 1 when anything must be fixed
    ERRORS_FOUND_STATUS: int = 1
    NOTHING_TO_FIX_STATUS: int = 0
    has_errors: bool = (Damage.count_errors(damage) > 0)
    exit_status: int = ERRORS_FOUND_STATUS if has_errors else NOTHING_TO_FIX_STATUS
    return exit_status


def _parse_options() -> argparse.Namespace:
    """Reads the command-line options.

    Returns:
        The options; skip_pointers is True when pointer checks should be left out.

    Raises:
        SystemExit: If the options are invalid, or --help was asked for.
    """
    # Define and read the one option
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="scan-for-brain-damage",
        description="Scan this brain for damage: broken rules, links, and pointers.",
    )
    parser.add_argument(
        SKIP_POINTERS_OPTION,
        action="store_true",
        help="don't check pointers against GitHub",
    )
    options: argparse.Namespace = parser.parse_args()
    return options


def _brain_root() -> Path:
    """The root folder of the brain this scan lives in.

    Returns:
        The folder above how-this-brain-works/, which holds this scan's folder.
    """
    # Go up from this scan's folder and from how-this-brain-works/
    root: Path = Path(__file__).resolve().parent.parent.parent
    return root


def _print_load_failure(error: BrainLoadError) -> None:
    """Explains why the brain couldn't be scanned.

    Args:
        error: Why it couldn't be loaded.
    """
    # Print to stderr, so the report stream stays clean
    print(f"Can't scan the brain: {error}", file=sys.stderr)


# Run the scan when executed
is_run_as_script: bool = (__name__ == "__main__")
if is_run_as_script:
    sys.exit(main())
