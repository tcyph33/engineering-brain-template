"""Tests for reading frontmatter: the note format's shape is read, and every other form is
rejected with the reason."""

from __future__ import annotations

import unittest
from types import MappingProxyType

from frontmatter import Frontmatter, FrontmatterState, ListItem
from note_with_frontmatter import note_with_frontmatter

# The end of every rejection that sends the reader to the note format.
NOTE_FORMAT_HINT: str = "see 'Note format' in how-this-brain-works/README.md"

# A reading: the frontmatter's state, and why it couldn't be read.
Reading = tuple[FrontmatterState, str]


def _read(*frontmatter_lines: str) -> Frontmatter:
    """Reads a note whose frontmatter holds the given lines.

    Args:
        frontmatter_lines: The lines between the '---' fences.

    Returns:
        The frontmatter as read.
    """
    # Build the note and read it
    frontmatter: Frontmatter = Frontmatter.read(note_with_frontmatter(*frontmatter_lines))
    return frontmatter


def _reading(*frontmatter_lines: str) -> Reading:
    """How frontmatter with the given lines reads: its state and its problem.

    Args:
        frontmatter_lines: The lines between the '---' fences.

    Returns:
        The state, and the problem (empty unless unreadable).
    """
    # Read the note and keep its state and problem
    frontmatter: Frontmatter = _read(*frontmatter_lines)
    reading: Reading = (frontmatter.state, frontmatter.problem)
    return reading


def _unreadable(problem: str) -> Reading:
    """The reading of frontmatter that can't be read for the given reason.

    Args:
        problem: Why it can't be read.

    Returns:
        The unreadable state with that problem.
    """
    # Pair the problem with the unreadable state
    reading: Reading = (FrontmatterState.UNREADABLE, problem)
    return reading


def _syntax_start_problem(value: str) -> str:
    """The problem with a value that starts with YAML syntax.

    Args:
        value: The value, as written after its comment is removed.

    Returns:
        The problem the reader gives.
    """
    # Name the value and its first character
    problem: str = (
        f"{value!r} starts with {value[0]!r}, which YAML reads as syntax rather than text; "
        "write the value plainly, without quotes, brackets, blocks, or markup at its start; "
        f"{NOTE_FORMAT_HINT}"
    )
    return problem


def _field_colon_problem(value: str) -> str:
    """The problem with a value holding a ':' YAML reads as a new field.

    Args:
        value: The value, as written.

    Returns:
        The problem the reader gives.
    """
    # Name the value
    problem: str = (
        f"{value!r} has a ':' followed by a space or the line's end, which YAML reads as "
        "starting another field; reword it"
    )
    return problem


def _unreadable_line_problem(stripped_line: str) -> str:
    """The problem with a line that isn't a field.

    Args:
        stripped_line: The line, without indentation.

    Returns:
        The problem the reader gives.
    """
    # Name the line
    problem: str = f"can't read frontmatter line: {stripped_line}; {NOTE_FORMAT_HINT}"
    return problem


def _list_line_problem(stripped_line: str) -> str:
    """The problem with a line under a list that isn't where the format puts it.

    Args:
        stripped_line: The line, without indentation.

    Returns:
        The problem the reader gives.
    """
    # Name the line and the rule
    problem: str = (
        f"can't read frontmatter line: {stripped_line}; list items line up under each other, "
        f"with no lists inside them; {NOTE_FORMAT_HINT}"
    )
    return problem


def _continuation_problem(field_name: str) -> str:
    """The problem with a field that has something other than a list below it.

    Args:
        field_name: The field.

    Returns:
        The problem the reader gives.
    """
    # Name the field
    problem: str = (
        f"{field_name} continues onto the lines below it; write a value on one line, or a "
        f"list of '- ' items under an empty field; {NOTE_FORMAT_HINT}"
    )
    return problem


# The problem with an empty list item.
EMPTY_ITEM_PROBLEM: str = "a list item is empty; remove it or give it a value"


class FrontmatterPresenceTest(unittest.TestCase):
    """Whether a note has a frontmatter block at all."""

    def test_note_without_an_opening_fence_has_no_frontmatter(self) -> None:
        """A note that doesn't start with '---' has absent frontmatter."""
        # Read a note with no block
        frontmatter: Frontmatter = Frontmatter.read("# Note\n")

        # Expect it absent
        self.assertEqual(frontmatter.state, FrontmatterState.ABSENT)

    def test_empty_note_has_no_frontmatter(self) -> None:
        """An empty file has absent frontmatter."""
        # Read an empty note
        frontmatter: Frontmatter = Frontmatter.read("")

        # Expect it absent
        self.assertEqual(frontmatter.state, FrontmatterState.ABSENT)

    def test_unclosed_frontmatter_is_unreadable(self) -> None:
        """A block opened with '---' and never closed can't be read."""
        # Read a note whose block never closes
        frontmatter: Frontmatter = Frontmatter.read("---\nsummary: One line.\n# Note\n")

        # Expect it unreadable, naming the missing fence
        self.assertEqual(
            (frontmatter.state, frontmatter.problem),
            _unreadable("frontmatter has no closing '---' line"),
        )

    def test_empty_block_is_readable_with_no_fields(self) -> None:
        """Two fences with nothing between them is frontmatter with no fields."""
        # Read an empty block
        frontmatter: Frontmatter = Frontmatter.read("---\n---\n")

        # Expect it readable and empty
        self.assertEqual(
            (frontmatter.state, frontmatter.field_names()), (FrontmatterState.READABLE, [])
        )

    def test_fences_with_trailing_spaces_still_count(self) -> None:
        """Spaces after a '---' fence don't stop it being a fence."""
        # Read a block whose fences have trailing spaces
        frontmatter: Frontmatter = Frontmatter.read("---  \nsummary: One line.\n---  \n")

        # Expect the field read
        self.assertEqual(frontmatter.text("summary"), "One line.")


class FrontmatterConsistencyTest(unittest.TestCase):
    """A Frontmatter can't be built in a state reading never gives."""

    def test_readable_frontmatter_with_a_problem_is_refused(self) -> None:
        """Only unreadable frontmatter has a problem."""
        # Build readable frontmatter with a problem, and expect a refusal
        with self.assertRaisesRegex(ValueError, "^readable frontmatter can't have problem"):
            Frontmatter(state=FrontmatterState.READABLE, problem="oops", _fields={})

    def test_unreadable_frontmatter_with_fields_is_refused(self) -> None:
        """Only readable frontmatter has fields."""
        # Build unreadable frontmatter with a field, and expect a refusal
        with self.assertRaisesRegex(ValueError, "^unreadable frontmatter can't have fields$"):
            Frontmatter(
                state=FrontmatterState.UNREADABLE, problem="oops", _fields={"summary": "x"}
            )


class FrontmatterValueTest(unittest.TestCase):
    """Reading one-line values, as the note format writes them."""

    def test_one_line_value_is_read(self) -> None:
        """A `name: value` line gives the value."""
        # Read a single field
        frontmatter: Frontmatter = _read("summary: One line.")

        # Expect its value
        self.assertEqual(frontmatter.text("summary"), "One line.")

    def test_trailing_comment_is_left_out_of_the_value(self) -> None:
        """A '#' after whitespace starts a comment, as in the manual's template."""
        # Read a value with a comment after it
        frontmatter: Frontmatter = _read("status: active       # optional")

        # Expect the value alone
        self.assertEqual(frontmatter.text("status"), "active")

    def test_hash_inside_a_word_stays_in_the_value(self) -> None:
        """A '#' with no space before it is text, not a comment."""
        # Read a value with a '#' inside a word
        frontmatter: Frontmatter = _read("summary: Written in C# only.")

        # Expect the whole value
        self.assertEqual(frontmatter.text("summary"), "Written in C# only.")

    def test_colon_inside_a_url_stays_in_the_value(self) -> None:
        """A ':' not followed by a space, as in a URL, is text."""
        # Read a URL value
        frontmatter: Frontmatter = _read("summary: See https://example.com/page.")

        # Expect the whole value
        self.assertEqual(frontmatter.text("summary"), "See https://example.com/page.")

    def test_markup_after_the_start_stays_in_the_value(self) -> None:
        """Only a value's first character can be YAML syntax; later ones are text."""
        # Read a value with emphasis in the middle
        frontmatter: Frontmatter = _read("summary: Read *this* first.")

        # Expect the whole value
        self.assertEqual(frontmatter.text("summary"), "Read *this* first.")

    def test_blank_lines_between_fields_are_skipped(self) -> None:
        """Blank lines inside the block don't stop the fields around them being read."""
        # Read fields separated by a blank line
        frontmatter: Frontmatter = _read("summary: One line.", "", "read-when: Always.")

        # Expect both fields
        self.assertEqual(frontmatter.field_names(), ["read-when", "summary"])


class FrontmatterAccessTest(unittest.TestCase):
    """Reading fields back from readable frontmatter."""

    def test_reading_a_list_as_a_value_is_refused(self) -> None:
        """Asking for a list field's single value is a caller's mistake."""
        # Read a note with a list field
        frontmatter: Frontmatter = _read("repos:", "  - owner/name")

        # Expect a refusal
        with self.assertRaisesRegex(ValueError, "^repos is a list; read it with items\\(\\)$"):
            frontmatter.text("repos")

    def test_reading_a_value_as_a_list_is_refused(self) -> None:
        """Asking for a single-value field's items is a caller's mistake."""
        # Read a note with a single-value field
        frontmatter: Frontmatter = _read("summary: One line.")

        # Expect a refusal
        with self.assertRaisesRegex(
            ValueError, "^summary is a single value; read it with text\\(\\)$"
        ):
            frontmatter.items("summary")

    def test_absent_field_reads_as_empty(self) -> None:
        """A field the note doesn't have is an empty value and an empty list."""
        # Read a note without the asked-for field
        frontmatter: Frontmatter = _read("summary: One line.")

        # Expect both readings empty
        self.assertEqual((frontmatter.text("status"), frontmatter.items("repos")), ("", ()))

    def test_empty_list_is_not_filled(self) -> None:
        """A list field with no items counts as empty."""
        # Read a note with an empty list field
        frontmatter: Frontmatter = _read("repos:")

        # Expect it not filled
        self.assertFalse(frontmatter.is_filled("repos"))


class FrontmatterListTest(unittest.TestCase):
    """Reading lists, as the note format writes them."""

    def test_map_items_are_read_as_maps(self) -> None:
        """The template's pointers read as one map per item."""
        # Read a pointers list
        frontmatter: Frontmatter = _read(
            "pointers:",
            "  - what: The thing",
            "    repo: org/repo-name",
            "    path: path/to/file",
            "  - what: A published doc",
            "    url: https://example.com/doc",
        )

        # Expect each item's fields
        expected_items: tuple[ListItem, ...] = (
            MappingProxyType({
                "what": "The thing", "repo": "org/repo-name", "path": "path/to/file"
            }),
            MappingProxyType({"what": "A published doc", "url": "https://example.com/doc"}),
        )
        self.assertEqual(frontmatter.items("pointers"), expected_items)

    def test_comments_in_a_list_are_left_out(self) -> None:
        """Comments after a list field and after an item's value, as in the template."""
        # Read a pointer with the template's comments
        frontmatter: Frontmatter = _read(
            "pointers:            # only if the note relies on something outside the brain",
            "  - what: The thing",
            "    verified: 2026-11-22 @ a1b2c3d  # date, plus commit for repo targets",
        )

        # Expect the values without the comments
        self.assertEqual(
            frontmatter.items("pointers"),
            (MappingProxyType({"what": "The thing", "verified": "2026-11-22 @ a1b2c3d"}),),
        )

    def test_plain_items_are_read_as_values(self) -> None:
        """Items without a field name read as plain values."""
        # Read a list of repositories
        frontmatter: Frontmatter = _read("repos:", "  - owner/first", "  - owner/second")

        # Expect each value
        self.assertEqual(frontmatter.items("repos"), ("owner/first", "owner/second"))

    def test_list_field_with_nothing_under_it_is_an_empty_list(self) -> None:
        """A list field written empty reads as a list with no items."""
        # Read an empty repos field
        frontmatter: Frontmatter = _read("repos:")

        # Expect it readable, with no items
        self.assertEqual(
            (frontmatter.state, frontmatter.items("repos")), (FrontmatterState.READABLE, ())
        )

    def test_list_fields_with_a_single_value_are_rejected(self) -> None:
        """Every field the manual writes as a list can't hold a single value."""
        # Read each list field written as a value, and expect its shape named
        list_field: str
        for list_field in ("repos", "occurrences", "pointers"):
            with self.subTest(list_field=list_field):
                self.assertEqual(
                    _reading(f"{list_field}: x"),
                    _unreadable(f"{list_field} must be a list"),
                )

    def test_single_value_fields_with_a_list_are_rejected(self) -> None:
        """Every field the manual writes as a value can't hold a list."""
        # Read each single-value field written as a list, and expect its shape named
        single_value_field: str
        for single_value_field in ("summary", "read-when", "depends-on", "status"):
            with self.subTest(single_value_field=single_value_field):
                self.assertEqual(
                    _reading(f"{single_value_field}:", "  - x"),
                    _unreadable(f"{single_value_field} must be a single value, not a list"),
                )


class FrontmatterRejectedValueTest(unittest.TestCase):
    """Values in forms YAML allows but the note format doesn't use."""

    def test_double_quoted_value_is_rejected(self) -> None:
        """Double quotes aren't part of the note format."""
        # Read a double-quoted value, and expect the quote named
        self.assertEqual(
            _reading('summary: "One line."'), _unreadable(_syntax_start_problem('"One line."'))
        )

    def test_single_quoted_value_is_rejected(self) -> None:
        """Single quotes aren't part of the note format."""
        # Read a single-quoted value, and expect the quote named
        self.assertEqual(
            _reading("summary: 'One line.'"), _unreadable(_syntax_start_problem("'One line.'"))
        )

    def test_bracketed_list_is_rejected(self) -> None:
        """A `[a, b]` list isn't part of the note format."""
        # Read a one-line list, and expect the bracket named
        self.assertEqual(
            _reading("repos: [owner/first, owner/second]"),
            _unreadable(_syntax_start_problem("[owner/first, owner/second]")),
        )

    def test_braced_map_is_rejected(self) -> None:
        """A `{a: b}` map isn't part of the note format."""
        # Read a one-line map, and expect the brace named
        self.assertEqual(
            _reading("summary: {a: b}"), _unreadable(_syntax_start_problem("{a: b}"))
        )

    def test_folded_block_is_rejected(self) -> None:
        """A `>` block isn't part of the note format."""
        # Read a folded block, and expect the block named
        self.assertEqual(
            _reading("summary: >", "  One line,", "  folded."),
            _unreadable(_syntax_start_problem(">")),
        )

    def test_literal_block_is_rejected(self) -> None:
        """A `|` block isn't part of the note format."""
        # Read a literal block, and expect the block named
        self.assertEqual(
            _reading("summary: |", "  One line."), _unreadable(_syntax_start_problem("|"))
        )

    def test_value_starting_with_markdown_emphasis_is_rejected(self) -> None:
        """A leading '*' is a YAML alias, not emphasis."""
        # Read a value starting with emphasis, and expect the '*' named
        self.assertEqual(
            _reading("read-when: *Always*"), _unreadable(_syntax_start_problem("*Always*"))
        )

    def test_value_starting_with_an_at_sign_is_rejected(self) -> None:
        """A leading '@' is reserved in YAML."""
        # Read a value starting with '@', and expect it named
        self.assertEqual(
            _reading("summary: @principles loads first."),
            _unreadable(_syntax_start_problem("@principles loads first.")),
        )

    def test_value_starting_with_a_backtick_is_rejected(self) -> None:
        """A leading '`' is reserved in YAML."""
        # Read a value starting with inline code, and expect the backtick named
        self.assertEqual(
            _reading("summary: `code` first."),
            _unreadable(_syntax_start_problem("`code` first.")),
        )

    def test_values_starting_with_other_yaml_syntax_are_rejected(self) -> None:
        """Tags, anchors, directives, flow marks, and block marks are syntax too."""
        # Read a value starting with each, and expect its first character named
        value: str
        for value in ("!important", "&anchor", "%directive", ", x", "]x", "? x", "- x", "-"):
            with self.subTest(value=value):
                self.assertEqual(
                    _reading(f"summary: {value}"), _unreadable(_syntax_start_problem(value))
                )

    def test_value_starting_with_a_hyphen_before_text_is_read(self) -> None:
        """A hyphen right before text, as in a negative number, isn't a list marker."""
        # Read a value starting with '-5'
        frontmatter: Frontmatter = _read("summary: -5 degrees.")

        # Expect the whole value
        self.assertEqual(frontmatter.text("summary"), "-5 degrees.")

    def test_value_wrapped_onto_the_next_line_is_rejected(self) -> None:
        """A value continued on an indented line isn't part of the note format."""
        # Read a wrapped value, and expect the wrap named
        self.assertEqual(
            _reading("summary: One line,", "  wrapped."),
            _unreadable(_continuation_problem("summary")),
        )

    def test_list_under_a_field_with_a_value_is_rejected(self) -> None:
        """A field can't have both a value and a list below it."""
        # Read a field with both, and expect the field named
        self.assertEqual(
            _reading("repos: owner/first", "  - owner/second"),
            _unreadable(_continuation_problem("repos")),
        )

    def test_value_with_a_colon_and_space_is_rejected(self) -> None:
        """A ': ' inside a value would make YAML read another field."""
        # Read a value with ': ' in it, and expect the colon named
        self.assertEqual(
            _reading("read-when: Any change: big or small."),
            _unreadable(_field_colon_problem("Any change: big or small.")),
        )

    def test_value_ending_in_a_colon_is_rejected(self) -> None:
        """A ':' at the end of a value would make YAML read another field."""
        # Read a value ending in ':', and expect the colon named
        self.assertEqual(
            _reading("summary: Steps:"), _unreadable(_field_colon_problem("Steps:"))
        )

    def test_plain_item_with_a_colon_and_space_is_rejected(self) -> None:
        """A list value with ': ' in it would read as a map in YAML."""
        # Read a list item with ': ' in it, and expect the colon named
        self.assertEqual(
            _reading("repos:", "  - Fix: this"), _unreadable(_field_colon_problem("Fix: this"))
        )


class FrontmatterRejectedLineTest(unittest.TestCase):
    """Lines that aren't in the note format's shape."""

    def test_whole_line_comment_is_rejected(self) -> None:
        """Comments only follow a value; a line of its own isn't part of the format."""
        # Read a comment line, and expect it named
        self.assertEqual(
            _reading("# A comment", "summary: One line."),
            _unreadable(_unreadable_line_problem("# A comment")),
        )

    def test_field_name_with_capitals_is_rejected(self) -> None:
        """Field names are lowercase words joined by hyphens."""
        # Read a capitalized field, and expect it named
        self.assertEqual(
            _reading("Summary: One line."),
            _unreadable(_unreadable_line_problem("Summary: One line.")),
        )

    def test_field_without_a_space_after_its_colon_is_rejected(self) -> None:
        """A field's value follows its colon and a space."""
        # Read a field with no space after the colon, and expect it named
        self.assertEqual(
            _reading("summary:One line."),
            _unreadable(_unreadable_line_problem("summary:One line.")),
        )

    def test_indented_first_line_is_rejected(self) -> None:
        """An indented line with no field above it belongs to nothing."""
        # Read a block starting with an indented line, and expect it named
        self.assertEqual(
            _reading("  summary: One line."),
            _unreadable(_unreadable_line_problem("summary: One line.")),
        )

    def test_tab_indented_line_is_rejected(self) -> None:
        """YAML indents only with spaces."""
        # Read a field indented with a tab, and expect it named
        self.assertEqual(
            _reading("\tsummary: One line."),
            _unreadable(_unreadable_line_problem("summary: One line.")),
        )

    def test_repeated_field_is_rejected(self) -> None:
        """A field written twice would leave one value silently ignored."""
        # Read a field written twice, and expect it named
        self.assertEqual(
            _reading("summary: First.", "summary: Second."),
            _unreadable("summary appears twice; merge them into one"),
        )

    def test_item_repeating_a_field_is_rejected(self) -> None:
        """A list item with a field written twice would leave one value ignored."""
        # Read an item with repo twice, and expect it named
        self.assertEqual(
            _reading("pointers:", "  - repo: owner/first", "    repo: owner/second"),
            _unreadable("a list item has repo twice; keep one"),
        )

    def test_nested_list_is_rejected(self) -> None:
        """Lists inside list items aren't part of the note format."""
        # Read an item with a list inside, and expect the line named
        self.assertEqual(
            _reading("pointers:", "  - what: The thing", "    - nested"),
            _unreadable(_list_line_problem("- nested")),
        )

    def test_item_line_not_lined_up_under_the_first_is_rejected(self) -> None:
        """An item's further lines line up under the text after its '- '."""
        # Read an item whose second line is indented too far, and expect the line named
        self.assertEqual(
            _reading("pointers:", "  - what: The thing", "     repo: owner/name"),
            _unreadable(_list_line_problem("repo: owner/name")),
        )

    def test_item_with_two_spaces_after_its_hyphen_is_rejected(self) -> None:
        """An item starts with a hyphen and exactly one space."""
        # Read an item with an extra space, and expect the line named
        self.assertEqual(
            _reading("repos:", "  -  owner/name"),
            _unreadable(_list_line_problem("-  owner/name")),
        )

    def test_hyphen_with_nothing_after_it_is_an_empty_item(self) -> None:
        """A lone hyphen is an item with no value."""
        # Read a lone hyphen, and expect an empty item named
        self.assertEqual(_reading("repos:", "  -"), _unreadable(EMPTY_ITEM_PROBLEM))

    def test_hyphen_and_space_with_nothing_after_is_an_empty_item(self) -> None:
        """A hyphen and a trailing space is still an item with no value."""
        # Read a hyphen with a trailing space, and expect an empty item named
        self.assertEqual(_reading("repos:", "  - "), _unreadable(EMPTY_ITEM_PROBLEM))

    def test_item_holding_only_a_comment_is_an_empty_item(self) -> None:
        """A comment isn't a value, so the item is empty."""
        # Read an item that's only a comment, and expect an empty item named
        self.assertEqual(_reading("repos:", "  - # later"), _unreadable(EMPTY_ITEM_PROBLEM))
