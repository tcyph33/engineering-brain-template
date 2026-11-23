"""Budget overrun: always-loaded files that together run over their line budget."""

from __future__ import annotations

from always_loaded_files import ROOT_README_PATH, AlwaysLoadedFiles
from brain import Brain
from damage import Damage, Severity
from note import Note


def find_budget_overrun(brain: Brain) -> list[Damage]:
    """Checks the always-loaded files stay within their line budget.

    Args:
        brain: The brain to scan.

    Returns:
        An error when the combined length is over budget.
    """
    # Add up every always-loaded file's lines
    always_loaded_line_count: int = 0
    loaded_note: Note
    for loaded_note in AlwaysLoadedFiles.follow(brain).notes:
        always_loaded_line_count += loaded_note.line_count

    # Report a total over the budget
    ALWAYS_LOADED_LINE_BUDGET: int = 150
    damage: list[Damage] = []
    is_over_budget: bool = (always_loaded_line_count > ALWAYS_LOADED_LINE_BUDGET)
    if is_over_budget:
        damage.append(Damage(
            Severity.ERROR,
            ROOT_README_PATH,
            f"the always-loaded files total {always_loaded_line_count} lines, over the "
            f"{ALWAYS_LOADED_LINE_BUDGET}-line budget; see 'How it's read' in the manual",
        ))
    return damage
