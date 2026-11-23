"""Tests for reading a note from disk: its encoding, its line endings, and leaving out code,
whose links and headings are only examples."""

from __future__ import annotations

import unittest

from brain import Brain
from link import Link
from note import Note
from scratch_brain import ScratchBrain

# Where each test's note lives.
NOTE_PATH: str = "lessons-learned/a-lesson.md"


def _read_note(test_case: unittest.TestCase, note_text: str) -> Note:
    """Writes one note into a scratch brain and reads it back.

    Args:
        test_case: The test the brain is for.
        note_text: The note's full contents.

    Returns:
        The note as the scan reads it.
    """
    # Load a brain holding only this note
    brain: Brain = ScratchBrain.load(test_case, {NOTE_PATH: note_text})
    note: Note = brain.notes[NOTE_PATH]
    return note


class NoteEncodingTest(unittest.TestCase):
    """Reading notes written by other editors."""

    def test_byte_order_mark_is_dropped(self) -> None:
        """A UTF-8 byte-order mark before the frontmatter doesn't hide it."""
        # Read a note starting with a byte-order mark
        note: Note = _read_note(self, "\ufeff---\nsummary: One line.\n---\n")

        # Expect its frontmatter read
        self.assertEqual(note.frontmatter.text("summary"), "One line.")

    def test_windows_line_endings_are_read_like_unix_ones(self) -> None:
        """A code block written with Windows line endings still closes at its fence."""
        # Read a note with Windows line endings and a link after a code block
        note: Note = _read_note(self, "```\r\ncode\r\n```\r\n[text](other.md)\r\n")

        # Expect the link after the block found
        self.assertEqual(note.links, (Link(target="other.md", anchor=""),))

    def test_line_count_counts_every_line(self) -> None:
        """The line count is the number of lines in the file."""
        # Read a three-line note
        note: Note = _read_note(self, "# Title\n\nText.\n")

        # Expect three lines
        self.assertEqual(note.line_count, 3)


class NoteCodeTest(unittest.TestCase):
    """Leaving code out of a note's links and headings."""

    def test_links_in_backtick_fences_are_left_out(self) -> None:
        """A link inside a ``` block is only an example."""
        # Read a note with a link in a code block
        note: Note = _read_note(self, "```\n[text](missing.md)\n```\n")

        # Expect no links
        self.assertEqual(note.links, ())

    def test_links_in_tilde_fences_are_left_out(self) -> None:
        """A link inside a ~~~ block is only an example."""
        # Read a note with a link in a tilde block
        note: Note = _read_note(self, "~~~\n[text](missing.md)\n~~~\n")

        # Expect no links
        self.assertEqual(note.links, ())

    def test_shorter_fence_inside_a_longer_one_does_not_close_it(self) -> None:
        """A ``` line inside a ```` block is part of the code."""
        # Read a note with a fence shown inside a longer fence
        note: Note = _read_note(self, "````\n```\n[text](missing.md)\n```\n````\n")

        # Expect no links
        self.assertEqual(note.links, ())

    def test_unclosed_fence_runs_to_the_end(self) -> None:
        """Everything after a fence that never closes is code."""
        # Read a note whose fence never closes
        note: Note = _read_note(self, "```\n[text](missing.md)\n")

        # Expect no links
        self.assertEqual(note.links, ())

    def test_links_after_a_closed_fence_are_found(self) -> None:
        """Closing a fence brings the text back."""
        # Read a note with a link after a code block
        note: Note = _read_note(self, "```\ncode\n```\n[text](other.md)\n")

        # Expect the link
        self.assertEqual(note.links, (Link(target="other.md", anchor=""),))

    def test_links_in_inline_code_are_left_out(self) -> None:
        """A link inside backticks is only an example."""
        # Read a note with a link in inline code
        note: Note = _read_note(self, "Write `[text](missing.md)` like this.\n")

        # Expect no links
        self.assertEqual(note.links, ())

    def test_headings_in_code_blocks_get_no_anchor(self) -> None:
        """A heading inside a code block is only an example."""
        # Read a note with a heading in a code block
        note: Note = _read_note(self, "```\n## Example\n```\n")

        # Expect no anchors
        self.assertEqual(note.anchors, frozenset())
