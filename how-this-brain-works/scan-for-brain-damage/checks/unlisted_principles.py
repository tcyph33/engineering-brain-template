"""Unlisted principles: principle files the principles README doesn't link to."""

from __future__ import annotations

from typing import Optional, cast

from brain import Brain, KnownNote
from damage import Damage, Severity
from link import Link
from note import Note
from note_kind import PRINCIPLE_FILE_KIND


def find_unlisted_principles(brain: Brain) -> list[Damage]:
    """Finds principle files the principles README doesn't link to.

    Args:
        brain: The brain to scan.

    Returns:
        An error for a missing principles README, or for each principle file it doesn't
        link to.
    """
    # Report a missing principles README, which every principle must be listed in
    PRINCIPLES_README_PATH: str = "principles/README.md"
    principles_readme: Optional[Note] = brain.notes.get(PRINCIPLES_README_PATH)
    has_principles_readme: bool = (principles_readme is not None)
    if not has_principles_readme:
        missing_readme_damage: list[Damage] = [Damage(
            Severity.ERROR,
            PRINCIPLES_README_PATH,
            "is missing; it lists every principle",
        )]
        return missing_readme_damage

    # Collect where the README's links lead, as brain-relative paths
    listing_note: Note = cast(Note, principles_readme)
    linked_paths: set[str] = set()
    link: Link
    for link in listing_note.links:
        linked_paths.add(link.path_from(listing_note.path))

    # Report each principle file none of them lead to
    damage: list[Damage] = []
    known_note: KnownNote
    for known_note in brain.known_notes():
        is_principle_file: bool = (known_note.kind == PRINCIPLE_FILE_KIND)
        is_linked: bool = (known_note.note.path in linked_paths)
        is_missing_from_readme: bool = (is_principle_file and (not is_linked))
        if is_missing_from_readme:
            damage.append(Damage(
                Severity.ERROR,
                known_note.note.path,
                f"no principle in {PRINCIPLES_README_PATH} links to this file",
            ))
    return damage
