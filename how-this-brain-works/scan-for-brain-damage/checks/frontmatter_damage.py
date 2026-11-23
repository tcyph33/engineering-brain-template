"""Frontmatter damage: frontmatter that's unreadable, missing, not allowed, or missing or
carrying the wrong fields for its kind of note."""

from __future__ import annotations

from brain import Brain, KnownNote
from damage import Damage, Severity
from frontmatter import FrontmatterState
from note import Note
from note_kind import FrontmatterRule


def find_frontmatter_damage(brain: Brain) -> list[Damage]:
    """Finds notes whose frontmatter doesn't match what their kind requires.

    Notes in places the manual doesn't define are left to the misplaced-files check.

    Args:
        brain: The brain to scan.

    Returns:
        An error for each unreadable, missing, or unexpected block, and for missing or
        disallowed fields.
    """
    # Check presence first; fields are only checked on readable frontmatter that belongs
    damage: list[Damage] = []
    known_note: KnownNote
    for known_note in brain.known_notes():
        presence_damage: list[Damage] = _find_presence_damage(known_note)
        damage.extend(presence_damage)
        has_presence_damage: bool = (len(presence_damage) > 0)
        is_readable: bool = (known_note.note.frontmatter.state == FrontmatterState.READABLE)
        has_fields_to_check: bool = ((not has_presence_damage) and is_readable)
        if not has_fields_to_check:
            continue
        damage.extend(_find_missing_field_damage(known_note))
        damage.extend(_find_disallowed_field_damage(known_note))
    return damage


def _find_presence_damage(known_note: KnownNote) -> list[Damage]:
    """Checks a note has frontmatter exactly when its kind needs it, and that it's readable.

    Args:
        known_note: A note and its kind.

    Returns:
        An error when the frontmatter is unreadable, missing, or not allowed.
    """
    # Report frontmatter that can't be read
    note: Note = known_note.note
    is_readable: bool = (note.frontmatter.state != FrontmatterState.UNREADABLE)
    if not is_readable:
        unreadable_damage: list[Damage] = [Damage(
            Severity.ERROR,
            note.path,
            note.frontmatter.problem,
        )]
        return unreadable_damage

    # Report frontmatter where the kind has none, or none where the kind needs it
    has_frontmatter: bool = (note.frontmatter.state == FrontmatterState.READABLE)
    kind_has_frontmatter: bool = (known_note.kind.frontmatter_rule != FrontmatterRule.NONE)
    is_presence_right: bool = (has_frontmatter == kind_has_frontmatter)
    damage: list[Damage] = []
    if not is_presence_right:
        expectation: str = "needs frontmatter" if kind_has_frontmatter else "has no frontmatter"
        damage.append(Damage(
            Severity.ERROR,
            note.path,
            f"a {known_note.kind.name} {expectation}",
        ))
    return damage


def _find_missing_field_damage(known_note: KnownNote) -> list[Damage]:
    """Finds required frontmatter fields a note leaves out or leaves empty.

    Args:
        known_note: A note with readable frontmatter, and its kind.

    Returns:
        An error listing the missing fields, when there are any.
    """
    # Report the missing fields
    damage: list[Damage] = []
    missing_fields: list[str] = known_note.note.missing_required_fields(known_note.kind)
    has_missing_fields: bool = (len(missing_fields) > 0)
    if has_missing_fields:
        damage.append(Damage(
            Severity.ERROR,
            known_note.note.path,
            f"a {known_note.kind.name} needs {', '.join(missing_fields)}",
        ))
    return damage


def _find_disallowed_field_damage(known_note: KnownNote) -> list[Damage]:
    """Finds frontmatter fields on a kind of note that allows only its required ones.

    Args:
        known_note: A note with readable frontmatter, and its kind.

    Returns:
        An error listing the fields to remove, when there are any.
    """
    # Only kinds limited to their required fields can have disallowed ones
    damage: list[Damage] = []
    is_limited_kind: bool = (known_note.kind.frontmatter_rule == FrontmatterRule.ONLY_REQUIRED)
    if not is_limited_kind:
        return damage

    # Report the extra fields
    extra_fields: list[str] = known_note.note.fields_beyond(known_note.kind)
    has_extra_fields: bool = (len(extra_fields) > 0)
    if has_extra_fields:
        damage.append(Damage(
            Severity.ERROR,
            known_note.note.path,
            f"a {known_note.kind.name} has only "
            f"{', '.join(sorted(known_note.kind.required_fields))}; "
            f"remove {', '.join(extra_fields)}",
        ))
    return damage
