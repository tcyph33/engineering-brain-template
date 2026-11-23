"""Damage: one problem the scan found in the brain."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """How urgently a piece of damage needs attention."""

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Damage:
    """One problem found in the brain.

    Attributes:
        severity: ERROR must be fixed before committing; WARNING needs a human look.
        location: The brain-relative path the problem is in.
        description: What is wrong, phrased so the fix is clear.
    """

    severity: Severity
    location: str
    description: str

    @property
    def is_error(self) -> bool:
        """Whether this damage must be fixed before committing.

        Returns:
            True for an error, False for a warning.
        """
        # Only errors block a commit
        is_error: bool = (self.severity == Severity.ERROR)
        return is_error

    @staticmethod
    def count_errors(damage: list[Damage]) -> int:
        """How many pieces of damage must be fixed before committing.

        Args:
            damage: Everything the scan found.

        Returns:
            The number of errors.
        """
        # Count each error
        error_count: int = 0
        found_damage: Damage
        for found_damage in damage:
            is_error: bool = (found_damage.is_error)
            if is_error:
                error_count += 1
        return error_count
