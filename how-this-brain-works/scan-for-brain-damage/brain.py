"""Brain: every file in the brain's git working tree, with its markdown read as notes."""

from __future__ import annotations

import posixpath
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, NamedTuple, cast

from note import Note, NoteReadError
from note_kind import NoteKind

# The folder that holds one folder per project.
PROJECTS_FOLDER: str = "projects"


class BrainLoadError(Exception):
    """Raised when the brain's files can't be listed or read."""


class KnownNote(NamedTuple):
    """A note in a place the manual defines, with its kind.

    Attributes:
        note: The note.
        kind: The kind of note the manual says it is.
    """

    note: Note
    kind: NoteKind


@dataclass(frozen=True)
class Brain:
    """The brain's files, read from its git working tree.

    Attributes:
        root: The brain's root folder, fully resolved.
        file_paths: Every brain-relative file path, tracked or new, exactly as git lists it.
            Stored read-only.
        notes: Every readable markdown file, by brain-relative path, in path order. Stored
            read-only.
        unreadable_notes: Why each markdown file that couldn't be read as UTF-8 text failed,
            by brain-relative path. Stored read-only.
        folder_paths: Every folder that holds a file, worked out from file_paths.
    """

    root: Path
    file_paths: frozenset[str]
    notes: Mapping[str, Note]
    unreadable_notes: Mapping[str, str]
    folder_paths: frozenset[str] = field(init=False)

    def __post_init__(self) -> None:
        """Stores read-only copies of the paths and notes, and works out the folders."""
        # Copy and freeze the paths and notes, keeping the notes in path order
        object.__setattr__(self, "file_paths", frozenset(self.file_paths))
        sorted_notes: dict[str, Note] = {}
        note_path: str
        for note_path in sorted(self.notes):
            sorted_notes[note_path] = self.notes[note_path]
        object.__setattr__(self, "notes", MappingProxyType(sorted_notes))
        object.__setattr__(self, "unreadable_notes", MappingProxyType(dict(self.unreadable_notes)))

        # Collect every folder that holds a file
        ROOT_FOLDER: str = ""
        folders: set[str] = set()
        file_path: str
        for file_path in self.file_paths:
            folder: str = posixpath.dirname(file_path)
            has_folder: bool = (folder != ROOT_FOLDER)
            while has_folder:
                folders.add(folder)
                folder = posixpath.dirname(folder)
                has_folder = (folder != ROOT_FOLDER)
        object.__setattr__(self, "folder_paths", frozenset(folders))

    @classmethod
    def load(cls, root: Path) -> Brain:
        """Reads every file in the brain's git working tree.

        Args:
            root: The brain's root folder; must be a git repository.

        Returns:
            The loaded brain.

        Raises:
            BrainLoadError: If the files can't be listed.
        """
        # List the files that exist, as git sees them, so ignored files are left out
        resolved_root: Path = root.resolve()
        file_paths: set[str] = set()
        listed_path: str
        for listed_path in _list_git_files(resolved_root):
            is_existing_file: bool = ((resolved_root / listed_path).is_file())
            if is_existing_file:
                file_paths.add(listed_path)

        # Read every markdown file as a note, recording any that can't be read so one bad
        # file doesn't hide the rest of the damage
        MARKDOWN_SUFFIX: str = ".md"
        notes: dict[str, Note] = {}
        unreadable_notes: dict[str, str] = {}
        file_path: str
        for file_path in sorted(file_paths):
            is_markdown: bool = (file_path.endswith(MARKDOWN_SUFFIX))
            if not is_markdown:
                continue
            try:
                notes[file_path] = Note.read(resolved_root, file_path)
            except NoteReadError as error:
                unreadable_notes[file_path] = str(error)

        # Build the brain
        brain: Brain = cls(
            root=resolved_root,
            file_paths=frozenset(file_paths),
            notes=notes,
            unreadable_notes=unreadable_notes,
        )
        return brain

    def contains_path(self, path: str) -> bool:
        """Whether a path is a file or folder in the brain, compared case-sensitively.

        Compares with git's file list rather than the disk, because macOS's disk ignores case
        and GitHub doesn't.

        Args:
            path: A normalized brain-relative path; "." is the brain's root.

        Returns:
            True when the path is the root, a file, or a folder holding files.
        """
        # Accept the root, a file, or a folder
        ROOT_PATH: str = "."
        is_root: bool = (path == ROOT_PATH)
        is_file: bool = (path in self.file_paths)
        is_folder: bool = (path in self.folder_paths)
        is_contained: bool = (is_root or is_file or is_folder)
        return is_contained

    def known_notes(self) -> list[KnownNote]:
        """The notes in places the manual defines, each with its kind, in path order.

        Returns:
            Each note whose kind is known.
        """
        # Pair each note with its kind, leaving out misplaced notes
        known_notes: list[KnownNote] = []
        note: Note
        for note in self.notes.values():
            has_kind: bool = (note.kind is not None)
            if has_kind:
                known_notes.append(KnownNote(note=note, kind=cast(NoteKind, note.kind)))
        return known_notes

    def project_names(self) -> frozenset[str]:
        """The folder names of every project in the brain.

        Returns:
            Each project's folder name under projects/.
        """
        # Collect the folder name of every file inside a project
        names: set[str] = set()
        file_path: str
        for file_path in self.file_paths:
            MINIMUM_PARTS_IN_A_PROJECT_FILE: int = 3
            path_parts: list[str] = file_path.split("/")
            is_under_projects: bool = (path_parts[0] == PROJECTS_FOLDER)
            is_deep_enough: bool = (len(path_parts) >= MINIMUM_PARTS_IN_A_PROJECT_FILE)
            is_inside_a_project: bool = (is_under_projects and is_deep_enough)
            if is_inside_a_project:
                PROJECT_NAME_POSITION: int = 1
                names.add(path_parts[PROJECT_NAME_POSITION])
        project_names: frozenset[str] = frozenset(names)
        return project_names


def _list_git_files(root: Path) -> list[str]:
    """Lists the tracked and new files in a git working tree.

    Args:
        root: The folder of a git repository.

    Returns:
        Each file's path relative to root, unquoted; deleted files may still be listed.

    Raises:
        BrainLoadError: If git isn't installed or root isn't a git repository.
    """
    # List the files git sees, NUL-separated so unusual names aren't quoted
    try:
        git_file_listing: subprocess.CompletedProcess[str] = subprocess.run(
            [
                "git", "-C", str(root), "ls-files", "-z",
                "--cached", "--others", "--exclude-standard",
            ],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise BrainLoadError("git isn't installed; the brain scan needs it") from error

    # Reject a folder that isn't a repository
    is_git_repository: bool = (git_file_listing.returncode == 0)
    if not is_git_repository:
        raise BrainLoadError(f"{root} isn't a git repository; the brain must be one")

    # Split the listing at its NUL separators
    PATH_SEPARATOR: str = "\0"
    paths: list[str] = []
    listed_path: str
    for listed_path in git_file_listing.stdout.split(PATH_SEPARATOR):
        has_listed_path: bool = (listed_path != "")
        if has_listed_path:
            paths.append(listed_path)
    return paths
