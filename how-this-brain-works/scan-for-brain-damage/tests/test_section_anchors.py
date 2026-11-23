"""Tests for working out the section anchors GitHub gives a note's headings."""

from __future__ import annotations

import unittest

from section_anchors import section_anchors


class HeadingFormTest(unittest.TestCase):
    """Which lines count as headings."""

    def test_hash_heading_gets_an_anchor(self) -> None:
        """A '#' heading's words become a hyphenated, lowercase anchor."""
        # Work out the anchor of one heading
        anchors: frozenset[str] = section_anchors("## Why It Matters\n")

        # Expect the slug
        self.assertEqual(anchors, frozenset({"why-it-matters"}))

    def test_closing_hashes_are_not_part_of_the_heading(self) -> None:
        """Hashes after a heading's text only close it."""
        # Work out the anchor of a closed heading
        anchors: frozenset[str] = section_anchors("## Why ##\n")

        # Expect the text alone
        self.assertEqual(anchors, frozenset({"why"}))

    def test_heading_indented_four_spaces_is_not_a_heading(self) -> None:
        """Four spaces of indentation make the line code, not a heading."""
        # Work out the anchors of an over-indented heading
        anchors: frozenset[str] = section_anchors("    ## Why\n")

        # Expect none
        self.assertEqual(anchors, frozenset())

    def test_text_underlined_with_equals_signs_is_a_heading(self) -> None:
        """A line underlined with '=' is a heading."""
        # Work out the anchor of an underlined heading
        anchors: frozenset[str] = section_anchors("Title\n=====\n")

        # Expect the slug
        self.assertEqual(anchors, frozenset({"title"}))

    def test_text_underlined_with_hyphens_is_a_heading(self) -> None:
        """A line of text underlined with '-' is a heading."""
        # Work out the anchor of an underlined heading
        anchors: frozenset[str] = section_anchors("Subtitle\n---\n")

        # Expect the slug
        self.assertEqual(anchors, frozenset({"subtitle"}))

    def test_list_item_above_hyphens_is_not_a_heading(self) -> None:
        """Hyphens below a list item are a rule, not an underline."""
        # Work out the anchors of a list item above a rule
        anchors: frozenset[str] = section_anchors("- item\n---\n")

        # Expect none
        self.assertEqual(anchors, frozenset())

    def test_hyphens_below_a_blank_line_are_not_an_underline(self) -> None:
        """A rule after a blank line underlines nothing."""
        # Work out the anchors of a lone rule
        anchors: frozenset[str] = section_anchors("Text\n\n---\n")

        # Expect none
        self.assertEqual(anchors, frozenset())


class AnchorSlugTest(unittest.TestCase):
    """How a heading's text becomes its anchor."""

    def test_repeated_headings_are_numbered(self) -> None:
        """The second and third of the same heading get '-1' and '-2'."""
        # Work out the anchors of a heading used three times
        anchors: frozenset[str] = section_anchors("## Why\n## Why\n## Why\n")

        # Expect the numbered anchors
        self.assertEqual(anchors, frozenset({"why", "why-1", "why-2"}))

    def test_emphasis_and_link_markup_are_dropped(self) -> None:
        """Bold marks and link syntax leave only the words."""
        # Work out the anchor of a marked-up heading
        anchors: frozenset[str] = section_anchors("## **Bold** [link](notes.md) `code`\n")

        # Expect the plain words
        self.assertEqual(anchors, frozenset({"bold-link-code"}))

    def test_underscores_inside_words_are_kept(self) -> None:
        """A snake_case name keeps its underscores."""
        # Work out the anchor of a snake_case heading
        anchors: frozenset[str] = section_anchors("## The file_paths field\n")

        # Expect the underscores kept
        self.assertEqual(anchors, frozenset({"the-file_paths-field"}))

    def test_punctuation_is_dropped(self) -> None:
        """Apostrophes, question marks, and the like aren't in anchors."""
        # Work out the anchor of a punctuated heading
        anchors: frozenset[str] = section_anchors("## What's here?\n")

        # Expect the punctuation gone
        self.assertEqual(anchors, frozenset({"whats-here"}))

    def test_letters_in_any_language_are_kept(self) -> None:
        """Accented letters stay in the anchor, lowercased."""
        # Work out the anchor of an accented heading
        anchors: frozenset[str] = section_anchors("## Café Menu\n")

        # Expect the accent kept
        self.assertEqual(anchors, frozenset({"café-menu"}))
