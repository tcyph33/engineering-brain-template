"""Pointer damage: pointers whose GitHub file is gone, lost its symbol, or changed since it
was verified. Web pointers (url only) aren't checked."""

from __future__ import annotations

from typing import Optional, cast

from brain import Brain
from damage import Damage, Severity
from github import GitHub, GitHubLookupError
from note import Note
from pointer import Pointer


def find_pointer_damage(brain: Brain, github: GitHub) -> list[Damage]:
    """Checks every pointer to a file in a GitHub repository.

    Args:
        brain: The brain to scan.
        github: A connection to GitHub.

    Returns:
        Damage for each broken or changed pointer.
    """
    # Check each repository pointer in every note
    damage: list[Damage] = []
    note: Note
    for note in brain.notes.values():
        pointer: Pointer
        for pointer in note.pointers.repository_pointers:
            damage.extend(_find_one_pointer_damage(github, note.path, pointer))
    return damage


def _find_one_pointer_damage(github: GitHub, note_path: str, pointer: Pointer) -> list[Damage]:
    """Checks one pointer's file still exists and still holds its symbol.

    Args:
        github: A connection to GitHub.
        note_path: The brain-relative path of the note holding the pointer.
        pointer: The pointer to check.

    Returns:
        An error if the file or symbol is gone; a warning if it changed since it was
        verified, or if it couldn't be checked.
    """
    # Fetch the target file
    try:
        found_text: Optional[str] = github.file_text(pointer.repository, pointer.path)
    except GitHubLookupError as error:
        lookup_damage: list[Damage] = [Damage(
            Severity.WARNING,
            note_path,
            f"pointer to {pointer.target} couldn't be checked: {error}",
        )]
        return lookup_damage

    # Report a target that's gone
    is_on_github: bool = (found_text is not None)
    if not is_on_github:
        gone_damage: list[Damage] = [Damage(
            Severity.ERROR,
            note_path,
            f"pointer to {pointer.name}: {pointer.target} isn't on GitHub, or your gh account "
            "can't see it; it was moved or deleted, hasn't been pushed, or is private",
        )]
        return gone_damage

    # Report a symbol that's no longer in the file
    file_text: str = cast(str, found_text)
    damage: list[Damage] = []
    has_symbol: bool = (pointer.symbol != "")
    is_symbol_in_file: bool = (pointer.symbol in file_text)
    is_symbol_missing: bool = (has_symbol and (not is_symbol_in_file))
    if is_symbol_missing:
        damage.append(Damage(
            Severity.ERROR,
            note_path,
            f"pointer to {pointer.name}: {pointer.symbol} is no longer in {pointer.target}",
        ))

    # Check whether the file changed since it was verified
    damage.extend(_find_change_since_verified(github, note_path, pointer))
    return damage


def _find_change_since_verified(github: GitHub, note_path: str, pointer: Pointer) -> list[Damage]:
    """Checks whether a pointer's file changed after it was last verified.

    Uses the commit in the verified stamp when there is one, or else its date.

    Args:
        github: A connection to GitHub.
        note_path: The brain-relative path of the note holding the pointer.
        pointer: The pointer to check.

    Returns:
        A warning if the file changed since it was verified, if there's no stamp, or if the
        check couldn't run.
    """
    # Report a pointer with nothing to compare against
    has_stamp: bool = (pointer.verified_date != "")
    if not has_stamp:
        unstamped_damage: list[Damage] = [Damage(
            Severity.WARNING,
            note_path,
            f"pointer to {pointer.target} has no verified date; verify it and add one",
        )]
        return unstamped_damage

    # Ask GitHub whether the file changed since then
    has_commit: bool = (pointer.verified_commit != "")
    has_changed: bool
    try:
        if has_commit:
            has_changed = github.has_file_changed_since_commit(
                pointer.repository, pointer.path, pointer.verified_commit
            )
        else:
            has_changed = github.has_file_changed_since_date(
                pointer.repository, pointer.path, pointer.verified_date
            )
    except GitHubLookupError as error:
        lookup_damage: list[Damage] = [Damage(
            Severity.WARNING,
            note_path,
            f"couldn't tell whether {pointer.target} changed: {error}",
        )]
        return lookup_damage

    # Report a change so the note gets re-verified
    damage: list[Damage] = []
    if has_changed:
        damage.append(Damage(
            Severity.WARNING,
            note_path,
            f"{pointer.target} changed since it was verified ({pointer.verified_stamp}); "
            "re-check the note and update verified",
        ))
    return damage
