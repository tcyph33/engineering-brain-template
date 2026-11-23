"""Broken links: relative links that leave the brain, or whose file or section doesn't
exist."""

from __future__ import annotations

from typing import Optional, cast

from brain import Brain
from damage import Damage, Severity
from link import Link
from note import Note


def find_broken_links(brain: Brain) -> list[Damage]:
    """Finds relative links that leave the brain or whose file or section doesn't exist.

    Args:
        brain: The brain to scan.

    Returns:
        An error for each broken link.
    """
    # Check every link in every note
    damage: list[Damage] = []
    note: Note
    for note in brain.notes.values():
        link: Link
        for link in note.links:
            damage.extend(_find_link_damage(brain, note, link))
    return damage


def _find_link_damage(brain: Brain, note: Note, link: Link) -> list[Damage]:
    """Checks one link stays in the brain and leads to a file or folder that exists.

    Args:
        brain: The brain being scanned.
        note: The note the link is in.
        link: The link to check.

    Returns:
        An error when the link leaves the brain or leads nowhere; otherwise any error from
        the section it names.
    """
    # Report a link that leaves the brain
    linked_path: str = link.path_from(note.path)
    is_parent_folder: bool = (linked_path == "..")
    is_above_brain: bool = (linked_path.startswith("../"))
    is_outside_brain: bool = (is_parent_folder or is_above_brain)
    if is_outside_brain:
        outside_damage: list[Damage] = [Damage(
            Severity.ERROR,
            note.path,
            f"links to {link.target}, which is outside the brain",
        )]
        return outside_damage

    # Report a link to a file or folder the brain doesn't have
    is_existing_target: bool = (brain.contains_path(linked_path))
    if not is_existing_target:
        missing_damage: list[Damage] = [Damage(
            Severity.ERROR,
            note.path,
            f"links to {link.target}, which doesn't exist (names are case-sensitive)",
        )]
        return missing_damage

    # Check the section it names, if any
    anchor_damage: list[Damage] = _find_anchor_damage(brain, note, link, linked_path)
    return anchor_damage


def _find_anchor_damage(brain: Brain, note: Note, link: Link, linked_path: str) -> list[Damage]:
    """Checks the section a link names exists in the note it leads to.

    Args:
        brain: The brain being scanned.
        note: The note the link is in.
        link: The link to check.
        linked_path: The brain-relative path the link leads to; must exist.

    Returns:
        An error when the linked note has no such section.
    """
    # Only links naming a section of a note can be checked
    damage: list[Damage] = []
    linked_note: Optional[Note] = brain.notes.get(linked_path)
    has_anchor: bool = (link.anchor != "")
    is_note_target: bool = (linked_note is not None)
    is_checkable_anchor: bool = (has_anchor and is_note_target)
    if not is_checkable_anchor:
        return damage

    # Report a section the note doesn't have
    is_existing_anchor: bool = (link.anchor in cast(Note, linked_note).anchors)
    if not is_existing_anchor:
        damage.append(Damage(
            Severity.ERROR,
            note.path,
            f"links to {link.target}#{link.anchor}, which has no such section",
        ))
    return damage
