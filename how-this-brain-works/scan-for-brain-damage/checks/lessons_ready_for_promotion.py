"""Lessons ready for promotion: lessons that have recurred often enough to suggest promoting
to a principle, a design tenet or domain concept, or a skill step."""

from __future__ import annotations

from brain import Brain, KnownNote
from damage import Damage, Severity
from note_kind import LESSON_KIND


def find_lessons_ready_for_promotion(brain: Brain) -> list[Damage]:
    """Finds lessons that have recurred often enough to suggest promoting.

    Args:
        brain: The brain to scan.

    Returns:
        A warning for each lesson at or past the promotion threshold.
    """
    # Report each lesson with enough occurrences
    damage: list[Damage] = []
    known_note: KnownNote
    for known_note in brain.known_notes():
        OCCURRENCES_TO_SUGGEST_PROMOTION: int = 3
        is_lesson: bool = (known_note.kind == LESSON_KIND)
        occurrence_count: int = known_note.note.occurrence_count
        has_recurred_enough: bool = (occurrence_count >= OCCURRENCES_TO_SUGGEST_PROMOTION)
        is_ready_for_promotion: bool = (is_lesson and has_recurred_enough)
        if is_ready_for_promotion:
            damage.append(Damage(
                Severity.WARNING,
                known_note.note.path,
                f"has {occurrence_count} occurrences; suggest promoting it (see 'Lessons')",
            ))
    return damage
