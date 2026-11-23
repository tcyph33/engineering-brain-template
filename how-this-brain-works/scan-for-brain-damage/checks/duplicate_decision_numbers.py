"""Duplicate decision numbers: one number used by more than one decision record."""

from __future__ import annotations

from typing import Optional

from brain import Brain
from damage import Damage, Severity
from note import Note


def find_duplicate_decision_numbers(brain: Brain) -> list[Damage]:
    """Finds decision numbers used by more than one decision record.

    Args:
        brain: The brain to scan.

    Returns:
        An error for each decision record whose number one earlier in path order uses.
    """
    # Track each number as decision records are seen, in path order
    damage: list[Damage] = []
    seen_numbers: set[str] = set()
    note_path: str
    for note_path in sorted(brain.notes):
        # Skip notes that aren't decision records
        note: Note = brain.notes[note_path]
        decision_number: Optional[str] = note.decision_number
        is_decision: bool = (decision_number is not None)
        if not is_decision:
            continue

        # Report a number an earlier decision record already uses
        is_duplicate: bool = (decision_number in seen_numbers)
        if is_duplicate:
            damage.append(Damage(
                Severity.ERROR,
                note.path,
                f"decision number {decision_number} is used twice",
            ))
        seen_numbers.add(str(decision_number))
    return damage
