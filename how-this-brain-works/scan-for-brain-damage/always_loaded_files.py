"""AlwaysLoadedFiles: the files Claude Code loads into every session, found by following the
root README's `@path` imports, and the imports of the files it imports."""

from __future__ import annotations

import collections
import posixpath
import re
from typing import NamedTuple, Optional, cast

from brain import Brain
from note import Note

# The README every session loads first; everything else always loaded is imported from it.
ROOT_README_PATH: str = "README.md"


class Import(NamedTuple):
    """One `@path` import, or the root README itself, which nothing imports.

    Attributes:
        importer: The brain-relative path of the note that imports it; None for the root
            README.
        path: The brain-relative path imported.
    """

    importer: Optional[str]
    path: str

    @property
    def is_root_readme(self) -> bool:
        """Whether this is the root README, loaded without any import.

        Returns:
            True when nothing imports it.
        """
        # Only the root README has no importer
        is_root_readme: bool = (self.importer is None)
        return is_root_readme


class AlwaysLoadedFiles(NamedTuple):
    """The always-loaded files, and imports that lead nowhere.

    Attributes:
        notes: The root README and every note it imports, directly or through others.
        missing_imports: Each import, including the root README itself, that isn't a note.
    """

    notes: tuple[Note, ...]
    missing_imports: tuple[Import, ...]

    @classmethod
    def follow(cls, brain: Brain) -> AlwaysLoadedFiles:
        """Follows imports from the root README to every always-loaded file.

        Args:
            brain: The brain being scanned.

        Returns:
            The notes found, and the imports that lead nowhere.
        """
        # Follow imports breadth-first from the root README, visiting each path once
        loaded_notes: list[Note] = []
        missing_imports: list[Import] = []
        imports_to_visit: collections.deque[Import] = collections.deque(
            [Import(importer=None, path=ROOT_README_PATH)]
        )
        visited_paths: set[str] = set()
        has_imports_to_visit: bool = True
        while has_imports_to_visit:
            next_import: Import = imports_to_visit.popleft()

            # Work out what this import is before marking its path visited
            is_visited: bool = (next_import.path in visited_paths)
            imported_note: Optional[Note] = brain.notes.get(next_import.path)
            is_existing_note: bool = (imported_note is not None)
            is_missing_import: bool = ((not is_visited) and (not is_existing_note))
            is_new_note: bool = ((not is_visited) and is_existing_note)

            # Record an import that leads nowhere
            if is_missing_import:
                missing_imports.append(next_import)

            # Load a newly found note and queue its own imports
            if is_new_note:
                found_note: Note = cast(Note, imported_note)
                loaded_notes.append(found_note)
                imports_to_visit.extend(_imports_in(found_note))

            # Mark the path visited, and continue while imports remain
            visited_paths.add(next_import.path)
            has_imports_to_visit = (len(imports_to_visit) > 0)

        # Return what was found
        always_loaded_files: AlwaysLoadedFiles = cls(
            notes=tuple(loaded_notes), missing_imports=tuple(missing_imports)
        )
        return always_loaded_files


def _imports_in(note: Note) -> list[Import]:
    """The `@path` imports a note makes, wherever they appear outside code.

    Like Claude Code, an import may sit on its own line or inside a sentence; an `@` inside
    a word, such as an email address, isn't one.

    Args:
        note: An always-loaded note.

    Returns:
        Each import, resolved relative to the note's folder.
    """
    # Find each @path that starts a word, dropping punctuation that ends a sentence
    IMPORT_PATTERN: re.Pattern[str] = re.compile(r"(?<![^\s(])@(?P<path>[^\s)]+)")
    SENTENCE_PUNCTUATION: str = ".,;:!?"
    imports: list[Import] = []
    import_match: re.Match[str]
    for import_match in IMPORT_PATTERN.finditer(note.readable_text):
        import_target: str = import_match.group("path").rstrip(SENTENCE_PUNCTUATION)
        joined_path: str = posixpath.join(posixpath.dirname(note.path), import_target)
        imports.append(Import(importer=note.path, path=posixpath.normpath(joined_path)))
    return imports
