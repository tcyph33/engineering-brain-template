"""Tests for finding links that lead outside the brain, or to files or sections that don't
exist."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.broken_links import find_broken_links
from damage import Damage, Severity
from scratch_brain import ScratchBrain

# The note each test's links are in.
LINKING_NOTE_PATH: str = "lessons-learned/README.md"


def _broken_links_in(test_case: unittest.TestCase, linking_text: str) -> list[Damage]:
    """Finds the broken links in a note, in a brain that also holds the linked note.

    Args:
        test_case: The test the brain is for.
        linking_text: The linking note's full contents.

    Returns:
        What the check reports.
    """
    # Load a brain with both notes, the linked one having one section, and check it
    LINKED_NOTE_PATH: str = "principles/README.md"
    LINKED_NOTE_TEXT: str = "# Principles\n\n## Belongs here\n"
    brain: Brain = ScratchBrain.load(test_case, {
        LINKING_NOTE_PATH: linking_text,
        LINKED_NOTE_PATH: LINKED_NOTE_TEXT,
    })
    damage: list[Damage] = find_broken_links(brain)
    return damage


def _broken_link_damage(description: str) -> list[Damage]:
    """The damage reported for one broken link in the linking note.

    Args:
        description: What's wrong with the link.

    Returns:
        The one error the check gives it.
    """
    # Build the expected error
    damage: list[Damage] = [Damage(Severity.ERROR, LINKING_NOTE_PATH, description)]
    return damage


class BrokenLinksTest(unittest.TestCase):
    """Which links are broken."""

    def test_link_to_a_missing_file_is_broken(self) -> None:
        """A link to a file the brain doesn't have leads nowhere."""
        # Check a link to a missing note
        damage: list[Damage] = _broken_links_in(self, "[text](missing.md)\n")

        # Expect it reported
        self.assertEqual(
            damage,
            _broken_link_damage(
                "links to missing.md, which doesn't exist (names are case-sensitive)"
            ),
        )

    def test_link_with_different_capitals_is_broken(self) -> None:
        """Names are case-sensitive, as on GitHub, even where the disk isn't."""
        # Check a link with the wrong capitals
        damage: list[Damage] = _broken_links_in(self, "[text](../principles/readme.md)\n")

        # Expect it reported
        self.assertEqual(
            damage,
            _broken_link_damage(
                "links to ../principles/readme.md, which doesn't exist (names are case-sensitive)"
            ),
        )

    def test_link_leaving_the_brain_is_broken(self) -> None:
        """A link that climbs above the brain's root leads outside it."""
        # Check a link that climbs too far
        damage: list[Damage] = _broken_links_in(self, "[text](../../etc/passwd)\n")

        # Expect it reported
        self.assertEqual(
            damage,
            _broken_link_damage(
                "links to ../../etc/passwd, which is outside the brain"
            ),
        )

    def test_link_to_a_missing_section_is_broken(self) -> None:
        """A link to a heading the note doesn't have leads nowhere."""
        # Check a link to a missing section
        damage: list[Damage] = _broken_links_in(self, "[text](../principles/README.md#nowhere)\n")

        # Expect it reported
        self.assertEqual(
            damage,
            _broken_link_damage(
                "links to ../principles/README.md#nowhere, which has no such section"
            ),
        )

    def test_link_to_a_missing_section_of_the_same_note_is_broken(self) -> None:
        """A '#section' link checks the note it's in."""
        # Check a same-note link to a missing section
        damage: list[Damage] = _broken_links_in(self, "# Lessons\n\n[text](#nowhere)\n")

        # Expect it reported
        self.assertEqual(
            damage,
            _broken_link_damage(
                "links to #nowhere, which has no such section"
            ),
        )

    def test_link_to_an_existing_note_is_not_broken(self) -> None:
        """A link to a note the brain has leads somewhere."""
        # Check a link to the linked note
        damage: list[Damage] = _broken_links_in(self, "[note](../principles/README.md)\n")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_link_to_an_existing_section_is_not_broken(self) -> None:
        """A link to a heading the note has leads somewhere."""
        # Check a link to the linked note's section
        damage: list[Damage] = _broken_links_in(
            self, "[section](../principles/README.md#belongs-here)\n"
        )

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_link_to_an_existing_folder_is_not_broken(self) -> None:
        """A link to a folder holding files leads somewhere."""
        # Check a link to the principles folder
        damage: list[Damage] = _broken_links_in(self, "[folder](../principles)\n")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_link_from_the_root_to_an_existing_note_is_not_broken(self) -> None:
        """A '/' link starts at the brain's root."""
        # Check a root-relative link
        damage: list[Damage] = _broken_links_in(self, "[root](/principles/README.md)\n")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_link_in_a_code_block_is_not_checked(self) -> None:
        """A link in a fenced block is only an example."""
        # Check a note whose only link is in a code block
        damage: list[Damage] = _broken_links_in(self, "```\n[text](missing.md)\n```\n")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_link_in_inline_code_is_not_checked(self) -> None:
        """A link in backticks is only an example."""
        # Check a note whose only link is in inline code
        damage: list[Damage] = _broken_links_in(self, "Write `[text](missing.md)` like this.\n")

        # Expect nothing reported
        self.assertEqual(damage, [])
