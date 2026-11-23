"""Misplaced files: files in places, or with names, the manual doesn't define."""

from __future__ import annotations

import re

from brain import Brain
from damage import Damage, Severity
from note_kind import LESSONS_FOLDER_PATTERN, NoteKind


def find_misplaced_files(brain: Brain) -> list[Damage]:
    """Finds files in places, or with names, the manual doesn't define.

    Args:
        brain: The brain to scan.

    Returns:
        An error for each misplaced file.
    """
    # Report each file that's neither a note nor another file the manual places
    damage: list[Damage] = []
    file_path: str
    for file_path in sorted(brain.file_paths):
        is_note_place: bool = (NoteKind.of(file_path) is not None)
        is_other_file_place: bool = (_is_other_file_place(file_path))
        is_known_place: bool = (is_note_place or is_other_file_place)
        if not is_known_place:
            damage.append(Damage(
                Severity.ERROR,
                file_path,
                "isn't a place or file name the manual defines; see 'Where knowledge goes' "
                "(names are kebab-case)",
            ))
    return damage


def _is_other_file_place(file_path: str) -> bool:
    """Whether a file that isn't a note has a place the manual defines.

    Args:
        file_path: A brain-relative path.

    Returns:
        True for the license and .gitignore at the root, a lessons folder's placeholder,
        and this scan's own code and tests, whose file names are lowercase snake_case.
    """
    # Match against each known non-note file
    OTHER_FILE_PATTERNS: tuple[re.Pattern[str], ...] = (
        re.compile(r"LICENSE"),
        re.compile(r"\.gitignore"),
        re.compile(rf"{LESSONS_FOLDER_PATTERN}/\.gitkeep"),
        re.compile(
            r"how-this-brain-works/scan-for-brain-damage/(checks/|tests/)?[a-z0-9_]+\.py"
        ),
    )
    pattern: re.Pattern[str]
    for pattern in OTHER_FILE_PATTERNS:
        is_match: bool = (pattern.fullmatch(file_path) is not None)
        if is_match:
            return True
    return False
