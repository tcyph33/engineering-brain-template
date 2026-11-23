"""Malformed pointers: pointers that don't fit the manual's pointer format."""

from __future__ import annotations

from brain import Brain
from damage import Damage, Severity
from note import Note


def find_malformed_pointers(brain: Brain) -> list[Damage]:
    """Finds pointers that don't fit the manual's pointer format.

    Args:
        brain: The brain to scan.

    Returns:
        An error for each malformed pointer.
    """
    # Report every reason found when the pointers were read
    damage: list[Damage] = []
    note: Note
    for note in brain.notes.values():
        malformed_reason: str
        for malformed_reason in note.pointers.malformed_reasons:
            damage.append(Damage(
                Severity.ERROR,
                note.path,
                f"{malformed_reason}; see 'Note format'",
            ))
    return damage
