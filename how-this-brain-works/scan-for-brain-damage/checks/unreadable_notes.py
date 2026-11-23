"""Unreadable notes: markdown files that couldn't be read as UTF-8 text."""

from __future__ import annotations

from brain import Brain
from damage import Damage, Severity


def find_unreadable_notes(brain: Brain) -> list[Damage]:
    """Finds markdown files that couldn't be read as UTF-8 text, so none of their other
    checks could run.

    Args:
        brain: The brain to scan.

    Returns:
        An error for each unreadable note.
    """
    # Report each note the brain couldn't read
    damage: list[Damage] = []
    note_path: str
    for note_path in sorted(brain.unreadable_notes):
        damage.append(Damage(
            Severity.ERROR,
            note_path,
            f"isn't readable UTF-8 text, so it couldn't be checked: "
            f"{brain.unreadable_notes[note_path]}",
        ))
    return damage
