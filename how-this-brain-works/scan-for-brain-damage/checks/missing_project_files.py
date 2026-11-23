"""Missing project files: projects without a file every project must have."""

from __future__ import annotations

from brain import PROJECTS_FOLDER, Brain
from damage import Damage, Severity


def find_missing_project_files(brain: Brain) -> list[Damage]:
    """Finds projects missing a file every project must have.

    Args:
        brain: The brain to scan.

    Returns:
        An error for each missing README.md or domain-concepts.md.
    """
    # Report each required file a project lacks
    damage: list[Damage] = []
    project_name: str
    for project_name in sorted(brain.project_names()):
        REQUIRED_PROJECT_FILES: tuple[str, ...] = ("README.md", "domain-concepts.md")
        required_file: str
        for required_file in REQUIRED_PROJECT_FILES:
            required_path: str = f"{PROJECTS_FOLDER}/{project_name}/{required_file}"
            has_required_file: bool = (required_path in brain.notes)
            if not has_required_file:
                damage.append(Damage(
                    Severity.ERROR,
                    f"{PROJECTS_FOLDER}/{project_name}/",
                    f"every project has {required_file}, even if it's nearly empty",
                ))
    return damage
