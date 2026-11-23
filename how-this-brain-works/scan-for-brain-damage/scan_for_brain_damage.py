"""The scan: every check that needs only the brain's own files, run in turn."""

from __future__ import annotations

from typing import Callable

from brain import Brain
from checks.broken_links import find_broken_links
from checks.budget_overrun import find_budget_overrun
from checks.duplicate_decision_numbers import find_duplicate_decision_numbers
from checks.frontmatter_damage import find_frontmatter_damage
from checks.lessons_ready_for_promotion import find_lessons_ready_for_promotion
from checks.malformed_pointers import find_malformed_pointers
from checks.misplaced_files import find_misplaced_files
from checks.missing_imports import find_missing_imports
from checks.missing_project_files import find_missing_project_files
from checks.quarantined_notes import find_quarantined_notes
from checks.references_to_missing_decisions import find_references_to_missing_decisions
from checks.unreadable_notes import find_unreadable_notes
from checks.unlisted_principles import find_unlisted_principles
from damage import Damage


def scan_for_brain_damage(brain: Brain) -> list[Damage]:
    """Runs every check that needs only the brain's own files.

    Pointers are checked separately, against GitHub, by checks.pointer_damage.

    Args:
        brain: The brain to scan.

    Returns:
        Everything the checks found.
    """
    # Run each check in turn
    FILE_CHECKS: tuple[Callable[[Brain], list[Damage]], ...] = (
        find_misplaced_files,
        find_unreadable_notes,
        find_frontmatter_damage,
        find_malformed_pointers,
        find_missing_project_files,
        find_broken_links,
        find_missing_imports,
        find_budget_overrun,
        find_unlisted_principles,
        find_duplicate_decision_numbers,
        find_references_to_missing_decisions,
        find_quarantined_notes,
        find_lessons_ready_for_promotion,
    )
    damage: list[Damage] = []
    file_check: Callable[[Brain], list[Damage]]
    for file_check in FILE_CHECKS:
        damage.extend(file_check(brain))
    return damage
