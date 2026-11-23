"""Tests for finding a note's links into the brain and working out where they lead."""

from __future__ import annotations

import unittest

from link import Link


class LinkFindingTest(unittest.TestCase):
    """Which links a note's text holds, and their targets and anchors."""

    def test_inline_link_is_found(self) -> None:
        """A `[text](path)` link gives its path."""
        # Find the link in a sentence
        links: tuple[Link, ...] = Link.all_in("See [the decision](decisions/0001-a.md).")

        # Expect its target
        self.assertEqual(links, (Link(target="decisions/0001-a.md", anchor=""),))

    def test_link_with_a_title_is_found(self) -> None:
        """A title after the path isn't part of the target."""
        # Find a link with a title
        links: tuple[Link, ...] = Link.all_in('[text](notes.md "A title")')

        # Expect the path alone
        self.assertEqual(links, (Link(target="notes.md", anchor=""),))

    def test_angle_bracketed_target_may_hold_spaces(self) -> None:
        """A `<path>` destination keeps its spaces."""
        # Find a bracketed link
        links: tuple[Link, ...] = Link.all_in("[text](<my notes.md>)")

        # Expect the whole path
        self.assertEqual(links, (Link(target="my notes.md", anchor=""),))

    def test_reference_definition_is_found(self) -> None:
        """A `[label]: path` line is a link too."""
        # Find a reference definition
        links: tuple[Link, ...] = Link.all_in("Text.\n\n[label]: notes.md\n")

        # Expect its target
        self.assertEqual(links, (Link(target="notes.md", anchor=""),))

    def test_link_text_may_hold_brackets(self) -> None:
        """Brackets inside link text don't hide the link."""
        # Find a link whose text has brackets
        links: tuple[Link, ...] = Link.all_in("[see [this] note](notes.md)")

        # Expect its target
        self.assertEqual(links, (Link(target="notes.md", anchor=""),))

    def test_web_link_is_left_out(self) -> None:
        """A link with a scheme, such as https:, doesn't lead into the brain."""
        # Find a web link
        links: tuple[Link, ...] = Link.all_in("[web](https://example.com)")

        # Expect none
        self.assertEqual(links, ())

    def test_mail_link_is_left_out(self) -> None:
        """A link with a scheme, such as mailto:, doesn't lead into the brain."""
        # Find a mail link
        links: tuple[Link, ...] = Link.all_in("[mail](mailto:a@example.com)")

        # Expect none
        self.assertEqual(links, ())

    def test_phone_link_is_left_out(self) -> None:
        """A link with a scheme, such as tel:, doesn't lead into the brain."""
        # Find a phone link
        links: tuple[Link, ...] = Link.all_in("[phone](tel:123)")

        # Expect none
        self.assertEqual(links, ())

    def test_placeholder_link_is_left_out(self) -> None:
        """The manual's `(...)` placeholder isn't a real link."""
        # Find a placeholder link
        links: tuple[Link, ...] = Link.all_in("see [why X is optional](...)")

        # Expect none
        self.assertEqual(links, ())

    def test_anchor_is_split_from_the_target(self) -> None:
        """A '#section' is the link's anchor, not part of its path."""
        # Find a link to a section
        links: tuple[Link, ...] = Link.all_in("[text](README.md#note-format)")

        # Expect the path and anchor apart
        self.assertEqual(links, (Link(target="README.md", anchor="note-format"),))

    def test_link_to_a_section_of_the_same_note_has_no_target(self) -> None:
        """A link that's only '#section' points into its own note."""
        # Find a same-note link
        links: tuple[Link, ...] = Link.all_in("[text](#why)")

        # Expect only the anchor
        self.assertEqual(links, (Link(target="", anchor="why"),))

    def test_percent_encoded_target_is_decoded(self) -> None:
        """'%20' and the like are read as the characters they stand for."""
        # Find an encoded link
        links: tuple[Link, ...] = Link.all_in("[text](my%20notes.md#caf%C3%A9)")

        # Expect the decoded path and anchor
        self.assertEqual(links, (Link(target="my notes.md", anchor="café"),))


class LinkPathTest(unittest.TestCase):
    """Where a link leads, as a brain-relative path."""

    def test_relative_target_starts_at_the_notes_folder(self) -> None:
        """A plain target is relative to the folder of the note it's in."""
        # Resolve a sibling link
        path: str = Link(target="other.md", anchor="").path_from("principles/README.md")

        # Expect the sibling's path
        self.assertEqual(path, "principles/other.md")

    def test_parent_target_climbs_out_of_the_notes_folder(self) -> None:
        """'..' moves up from the note's folder."""
        # Resolve a parent link
        path: str = Link(target="../README.md", anchor="").path_from("principles/README.md")

        # Expect the root README
        self.assertEqual(path, "README.md")

    def test_slash_target_starts_at_the_brains_root(self) -> None:
        """A target starting with '/' is relative to the brain's root."""
        # Resolve a root-relative link
        path: str = Link(target="/principles/README.md", anchor="").path_from(
            "projects/a/README.md"
        )

        # Expect the path from the root
        self.assertEqual(path, "principles/README.md")

    def test_empty_target_is_the_note_itself(self) -> None:
        """A same-note link leads to the note it's in."""
        # Resolve a same-note link
        path: str = Link(target="", anchor="why").path_from("principles/README.md")

        # Expect the note's own path
        self.assertEqual(path, "principles/README.md")

    def test_target_climbing_past_the_root_leaves_the_brain(self) -> None:
        """A path that climbs above the root starts with '..'."""
        # Resolve a link that climbs too far
        path: str = Link(target="../../etc/passwd", anchor="").path_from("principles/README.md")

        # Expect a path outside the brain
        self.assertEqual(path, "../etc/passwd")
