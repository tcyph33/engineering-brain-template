"""Quarantined notes: notes marked stale or unverified, which agents won't rely on."""

from __future__ import annotations

from brain import Brain
from damage import Damage, Severity
from note import Note


def find_quarantined_notes(brain: Brain) -> list[Damage]:
    """Finds notes marked stale or unverified, which agents won't rely on.

    Args:
        brain: The brain to scan.

    Returns:
        A warning for each quarantined note.
    """
    # Report each note whose status quarantines it
    damage: list[Damage] = []
    note: Note
    for note in brain.notes.values():
        QUARANTINED_STATUSES: frozenset[str] = frozenset({"stale", "unverified"})
        is_quarantined: bool = (note.status in QUARANTINED_STATUSES)
        if is_quarantined:
            damage.append(Damage(
                Severity.WARNING,
                note.path,
                f"is quarantined (status: {note.status}); verify it or fix it",
            ))
    return damage
