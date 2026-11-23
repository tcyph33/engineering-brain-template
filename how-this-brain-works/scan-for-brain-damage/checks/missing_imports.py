"""Missing imports: a missing root README, or always-loaded imports that lead nowhere."""

from __future__ import annotations

from typing import cast

from always_loaded_files import AlwaysLoadedFiles, Import
from brain import Brain
from damage import Damage, Severity


def find_missing_imports(brain: Brain) -> list[Damage]:
    """Finds a missing root README, and always-loaded imports that lead nowhere.

    Args:
        brain: The brain to scan.

    Returns:
        An error for each missing file.
    """
    # Report each import, or the root README itself, that isn't a note
    damage: list[Damage] = []
    missing_import: Import
    for missing_import in AlwaysLoadedFiles.follow(brain).missing_imports:
        is_imported_by_a_note: bool = (not missing_import.is_root_readme)
        if is_imported_by_a_note:
            damage.append(Damage(
                Severity.ERROR,
                cast(str, missing_import.importer),
                f"imports {missing_import.path}, which isn't a note in the brain",
            ))
        else:
            damage.append(Damage(
                Severity.ERROR,
                missing_import.path,
                "the brain has no root README, so nothing in it loads",
            ))
    return damage
