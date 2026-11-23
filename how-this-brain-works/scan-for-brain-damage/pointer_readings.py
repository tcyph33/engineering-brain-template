"""PointerReadings: a note's pointers, checked against the manual's pointer format and sorted
into the ones that can be checked against GitHub and the ones that are malformed."""

from __future__ import annotations

import datetime
import re
from typing import Mapping, NamedTuple, Optional, cast

from frontmatter import Frontmatter, ListItem
from pointer import Pointer

# A pointer's field names, as the manual's note format writes them.
WHAT_KEY: str = "what"
REPOSITORY_KEY: str = "repo"
PATH_KEY: str = "path"
SYMBOL_KEY: str = "symbol"
URL_KEY: str = "url"
VERIFIED_KEY: str = "verified"


class PointerReadings(NamedTuple):
    """A note's pointers, sorted by what can be done with them.

    Web pointers (url only) are well-formed but aren't checked, so they're in neither list.

    Attributes:
        repository_pointers: Well-formed pointers to repository files, which can be checked.
        malformed_reasons: Why each malformed pointer doesn't fit the manual's format.
    """

    repository_pointers: tuple[Pointer, ...]
    malformed_reasons: tuple[str, ...]

    @classmethod
    def read(cls, frontmatter: Frontmatter) -> PointerReadings:
        """Reads and sorts a note's pointers.

        Args:
            frontmatter: The note's frontmatter, with its field shapes already checked.

        Returns:
            The repository pointers and the reasons any pointer is malformed.
        """
        # Read each item as a repository pointer, a web pointer, or a malformed one
        POINTERS_FIELD: str = "pointers"
        repository_pointers: list[Pointer] = []
        malformed_reasons: list[str] = []
        pointer_item: ListItem
        for pointer_item in frontmatter.items(POINTERS_FIELD):
            pointer_reading: _PointerReading = _read_pointer(pointer_item)
            is_malformed: bool = (pointer_reading.problem is not None)
            is_repository_pointer: bool = (pointer_reading.pointer is not None)
            if is_malformed:
                malformed_reasons.append(cast(str, pointer_reading.problem))
            elif is_repository_pointer:
                repository_pointers.append(cast(Pointer, pointer_reading.pointer))
        readings: PointerReadings = cls(
            repository_pointers=tuple(repository_pointers),
            malformed_reasons=tuple(malformed_reasons),
        )
        return readings


class _PointerReading(NamedTuple):
    """What one pointers item turned out to be.

    Attributes:
        pointer: The repository pointer, when the item is a well-formed one.
        problem: Why the item is malformed, when it is.
    Both are None for a well-formed web pointer.
    """

    pointer: Optional[Pointer]
    problem: Optional[str]


def _read_pointer(pointer_item: ListItem) -> _PointerReading:
    """Reads one pointers item as a repository pointer, a web pointer, or a malformed one.

    Args:
        pointer_item: One item of a note's pointers field.

    Returns:
        The pointer, or the problem, or neither for a web pointer.
    """
    # A pointer must be a map of fields
    is_map: bool = (isinstance(pointer_item, Mapping))
    if not is_map:
        not_a_map: _PointerReading = _PointerReading(
            pointer=None, problem=f"a pointer must be a map of fields, not {pointer_item!r}"
        )
        return not_a_map

    # A web pointer is well-formed; anything else must name a repository
    pointer_fields: Mapping[str, str] = cast(Mapping[str, str], pointer_item)
    has_url: bool = (URL_KEY in pointer_fields)
    has_repository: bool = (REPOSITORY_KEY in pointer_fields)
    is_web_pointer: bool = (has_url and (not has_repository))
    if is_web_pointer:
        web_pointer: _PointerReading = _PointerReading(pointer=None, problem=None)
        return web_pointer
    if not has_repository:
        no_target: _PointerReading = _PointerReading(
            pointer=None, problem="each pointer needs repo and path, or url"
        )
        return no_target
    repository_pointer: _PointerReading = _read_repository_pointer(pointer_fields)
    return repository_pointer


def _read_repository_pointer(pointer_fields: Mapping[str, str]) -> _PointerReading:
    """Checks a repository pointer's fields against the manual's format and builds it.

    Args:
        pointer_fields: A pointer's fields, including repo.

    Returns:
        The pointer when it's well-formed, otherwise the problem.
    """
    # Check the repository and path
    REPOSITORY_PATTERN: re.Pattern[str] = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
    repository: str = pointer_fields.get(REPOSITORY_KEY, "")
    is_repository_valid: bool = (REPOSITORY_PATTERN.fullmatch(repository) is not None)
    if not is_repository_valid:
        bad_repository: _PointerReading = _PointerReading(
            pointer=None, problem=f"pointer repo must be owner/name, not {repository!r}"
        )
        return bad_repository
    path: str = pointer_fields.get(PATH_KEY, "")
    has_path: bool = (path != "")
    if not has_path:
        no_path: _PointerReading = _PointerReading(
            pointer=None, problem=f"pointer to {repository} needs a path"
        )
        return no_path

    # Check the verified stamp, when there is one
    verified_stamp: str = pointer_fields.get(VERIFIED_KEY, "")
    stamp_problem: Optional[str] = _verified_stamp_problem(verified_stamp)
    has_stamp_problem: bool = (stamp_problem is not None)
    if has_stamp_problem:
        bad_stamp: _PointerReading = _PointerReading(pointer=None, problem=stamp_problem)
        return bad_stamp

    # Build the pointer
    stamp_date: str
    stamp_commit: str
    stamp_date, stamp_commit = _split_verified_stamp(verified_stamp)
    pointer: Pointer = Pointer(
        description=pointer_fields.get(WHAT_KEY, ""),
        repository=repository,
        path=path,
        symbol=pointer_fields.get(SYMBOL_KEY, ""),
        verified_stamp=verified_stamp,
        verified_date=stamp_date,
        verified_commit=stamp_commit,
    )
    well_formed: _PointerReading = _PointerReading(pointer=pointer, problem=None)
    return well_formed


def _verified_stamp_problem(verified_stamp: str) -> Optional[str]:
    """Checks a verified stamp is empty, "YYYY-MM-DD", or "YYYY-MM-DD @ commit".

    Args:
        verified_stamp: A pointer's verified field, as written; may be empty.

    Returns:
        Why the stamp is malformed, or None when it's fine.
    """
    # An empty stamp is allowed; the pointer check warns about it later
    has_stamp: bool = (verified_stamp != "")
    if not has_stamp:
        return None

    # Check the date
    stamp_date: str
    stamp_commit: str
    stamp_date, stamp_commit = _split_verified_stamp(verified_stamp)
    try:
        datetime.date.fromisoformat(stamp_date)
    except ValueError:
        date_problem: str = f"verified must start with a YYYY-MM-DD date, not {verified_stamp!r}"
        return date_problem

    # Check the commit, when there is one
    COMMIT_PATTERN: re.Pattern[str] = re.compile(r"[0-9a-f]{7,40}")
    has_commit: bool = (stamp_commit != "")
    is_commit_valid: bool = (COMMIT_PATTERN.fullmatch(stamp_commit) is not None)
    is_commit_malformed: bool = (has_commit and (not is_commit_valid))
    if is_commit_malformed:
        commit_problem: str = f"verified commit must be a hex hash, not {stamp_commit!r}"
        return commit_problem
    return None


def _split_verified_stamp(verified_stamp: str) -> tuple[str, str]:
    """Splits a verified stamp into its date and commit.

    Args:
        verified_stamp: A pointer's verified field, as written.

    Returns:
        (date, commit), each stripped; the commit is empty when the stamp has none.
    """
    # Split at the separator and trim each side
    VERIFIED_STAMP_SEPARATOR: str = "@"
    stamp_date: str
    stamp_commit: str
    stamp_date, _, stamp_commit = verified_stamp.partition(VERIFIED_STAMP_SEPARATOR)
    stamp_parts: tuple[str, str] = (stamp_date.strip(), stamp_commit.strip())
    return stamp_parts
