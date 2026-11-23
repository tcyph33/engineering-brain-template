"""Pointer: a note's checked pointer to a file in a GitHub repository."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pointer:
    """A note's pointer to a file in a GitHub repository, already checked for format.

    Attributes:
        description: What the target is (the pointer's `what`).
        repository: The repository, as "owner/name".
        path: The file's path in the repository.
        symbol: A name the file must still contain; empty when the pointer names none.
        verified_stamp: The pointer's verified field as written; empty when it has none.
        verified_date: The verified day, as YYYY-MM-DD; empty when there's no stamp.
        verified_commit: The verified commit; empty when the stamp records only a date.
    """

    description: str
    repository: str
    path: str
    symbol: str
    verified_stamp: str
    verified_date: str
    verified_commit: str

    @property
    def target(self) -> str:
        """The repository and path together, for messages.

        Returns:
            "owner/name/path/to/file".
        """
        # Name the target by repository and path
        full_target: str = f"{self.repository}/{self.path}"
        return full_target

    @property
    def name(self) -> str:
        """What to call the pointer in messages: its description, or else its target.

        Returns:
            The description when it has one, otherwise the target.
        """
        # Prefer the description
        has_description: bool = (self.description != "")
        pointer_name: str = self.description if has_description else self.target
        return pointer_name
