"""References to missing decisions: decision numbers mentioned that no decision record has."""

from __future__ import annotations

import re
from typing import Optional

from brain import Brain
from damage import Damage, Severity
from note import Note


def find_references_to_missing_decisions(brain: Brain) -> list[Damage]:
    """Finds references to decision numbers no decision record has.

    A reference is a four-digit number starting with 0, as in "see 0013", outside code.
    Gaps in the numbering are fine: a decision whose question stopped mattering is deleted
    and its number left unused. Numbers from 1000 up aren't recognized as references.

    Args:
        brain: The brain to scan.

    Returns:
        An error for each note's reference to a missing decision.
    """
    # Report each number referenced outside code that doesn't exist
    DECISION_REFERENCE_PATTERN: re.Pattern[str] = re.compile(
        r"""
        (?<![\w./@:-])   # not part of a word, path, version, commit, or time
        (0\d{3})         # a four-digit number starting with 0, as in "see 0013"
        (?![\w-])        # not followed by more of a word or a file name's dash
        """,
        flags=re.VERBOSE,
    )
    existing_numbers: set[str] = _existing_decision_numbers(brain)
    damage: list[Damage] = []
    note: Note
    for note in brain.notes.values():
        referenced_numbers: set[str] = set(DECISION_REFERENCE_PATTERN.findall(note.readable_text))
        referenced_number: str
        for referenced_number in sorted(referenced_numbers - existing_numbers):
            damage.append(Damage(
                Severity.ERROR,
                note.path,
                f"refers to decision {referenced_number}, which doesn't exist",
            ))
    return damage


def _existing_decision_numbers(brain: Brain) -> set[str]:
    """The numbers of every decision record in the brain.

    Args:
        brain: The brain to scan.

    Returns:
        Each decision record's four-digit number.
    """
    # Collect each decision record's number
    existing_numbers: set[str] = set()
    note: Note
    for note in brain.notes.values():
        decision_number: Optional[str] = note.decision_number
        is_decision: bool = (decision_number is not None)
        if is_decision:
            existing_numbers.add(str(decision_number))
    return existing_numbers
