"""The damage report: what the scan found, printed errors first, with a summary."""

from __future__ import annotations

from damage import Damage, Severity


def print_damage_report(damage: list[Damage]) -> None:
    """Prints the damage found, errors first, and a summary.

    Args:
        damage: Everything the scan found.
    """
    # Say so when there's nothing to report
    has_damage: bool = (len(damage) > 0)
    if not has_damage:
        print("No brain damage found.")
        return

    # Print each problem
    found_damage: Damage
    for found_damage in sorted(damage, key=_report_order):
        SEVERITY_COLUMN_WIDTH: int = 8
        severity_label: str = found_damage.severity.value.ljust(SEVERITY_COLUMN_WIDTH)
        print(f"{severity_label}{found_damage.location}: {found_damage.description}")

    # Summarize, saying whether anything blocks a commit
    error_count: int = Damage.count_errors(damage)
    warning_count: int = (len(damage) - error_count)
    print(f"\n{error_count} errors, {warning_count} warnings.")
    has_errors: bool = (error_count > 0)
    if has_errors:
        print("Fix the errors before committing.")


def _report_order(found_damage: Damage) -> tuple[int, str]:
    """The order the report lists damage in: errors first, then by location.

    Args:
        found_damage: Something the scan found.

    Returns:
        A sort key.
    """
    # Rank by severity, then location
    SEVERITY_REPORT_RANK: dict[Severity, int] = {Severity.ERROR: 0, Severity.WARNING: 1}
    sort_key: tuple[int, str] = (
        SEVERITY_REPORT_RANK[found_damage.severity], found_damage.location
    )
    return sort_key
