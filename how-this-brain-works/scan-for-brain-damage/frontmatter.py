"""Frontmatter: reading a note's frontmatter block, which must have exactly the shape the
manual's note format shows.

That shape: top-level `name: value` fields, each value on one line; lists under an empty
field, whose items are plain values (`- value`) or small maps (`- name: value` followed by
`name: value` lines lined up under the first); and `# comments` after whitespace. Anything
else YAML allows is rejected: values starting with YAML syntax (quotes, `[a, b]` lists, `>`
and `|` blocks, `*`, `&`, `!`, `@`, and the like), values holding a ':' YAML would read as a
new field, values wrapped onto more lines, and nested lists. So every note reads the same to
this scan as to GitHub.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping, NamedTuple, Optional, Union, cast

# A frontmatter list item is a plain value or a small map of fields.
ListItem = Union[str, Mapping[str, str]]
# A frontmatter field is a plain value or a list of items.
FieldValue = Union[str, tuple[ListItem, ...]]

# Fields the manual writes as lists; written with nothing under them, they're empty lists.
LIST_FIELDS: frozenset[str] = frozenset({"repos", "occurrences", "pointers"})

# Where a rejected form sends the reader.
NOTE_FORMAT_HINT: str = "see 'Note format' in how-this-brain-works/README.md"

# What indents a line; YAML allows only spaces.
INDENTATION_CHARACTER: str = " "

# What starts a list item: a hyphen, then one space and the item.
LIST_ITEM_MARKER: str = "- "


class FrontmatterError(Exception):
    """Raised when a note's frontmatter can't be read."""


class FrontmatterState(Enum):
    """Whether a note has frontmatter, and whether it could be read."""

    ABSENT = "absent"
    READABLE = "readable"
    UNREADABLE = "unreadable"


@dataclass(frozen=True)
class Frontmatter:
    """A note's frontmatter, as read, with every field already checked for its shape.

    Read fields through text(), items(), is_filled(), and field_names().

    Attributes:
        state: Whether the frontmatter is absent, readable, or unreadable.
        problem: Why it couldn't be read; empty unless the state is UNREADABLE.
        _fields: Each field's value; empty unless the state is READABLE. Stored read-only.
    """

    state: FrontmatterState
    problem: str
    _fields: Mapping[str, FieldValue]

    def __post_init__(self) -> None:
        """Checks the state, problem, and fields agree, and stores a read-only copy of the
        fields, so no caller's dict is shared.

        Raises:
            ValueError: If there's a problem without the UNREADABLE state, or the reverse,
                or fields without the READABLE state.
        """
        # A problem goes with UNREADABLE, and only with it
        is_unreadable: bool = (self.state == FrontmatterState.UNREADABLE)
        has_problem: bool = (self.problem != "")
        is_problem_consistent: bool = (has_problem == is_unreadable)
        if not is_problem_consistent:
            raise ValueError(f"{self.state.value} frontmatter can't have problem {self.problem!r}")

        # Fields go only with READABLE
        is_readable: bool = (self.state == FrontmatterState.READABLE)
        has_fields: bool = (len(self._fields) > 0)
        has_misplaced_fields: bool = (has_fields and (not is_readable))
        if has_misplaced_fields:
            raise ValueError(f"{self.state.value} frontmatter can't have fields")

        # Copy and freeze the fields
        object.__setattr__(self, "_fields", MappingProxyType(dict(self._fields)))

    @classmethod
    def read(cls, text: str) -> Frontmatter:
        """Reads a note's frontmatter, keeping the reason when it can't be read.

        Args:
            text: A note's full contents, with Unix line endings.

        Returns:
            The frontmatter: absent, readable with its fields, or unreadable with the problem.
        """
        # Find the frontmatter block
        try:
            block_lines: Optional[list[str]] = _block_lines(text)
        except FrontmatterError as error:
            unclosed: Frontmatter = cls(
                state=FrontmatterState.UNREADABLE, problem=str(error), _fields={}
            )
            return unclosed
        has_block: bool = (block_lines is not None)
        if not has_block:
            absent: Frontmatter = cls(state=FrontmatterState.ABSENT, problem="", _fields={})
            return absent

        # Parse its fields, read empty list fields as empty lists, and check their shapes
        try:
            parsed_fields: dict[str, FieldValue] = _parse_block(cast(list[str], block_lines))
            fields: dict[str, FieldValue] = _with_empty_lists(parsed_fields)
            _check_field_shapes(fields)
        except FrontmatterError as error:
            unparsable: Frontmatter = cls(
                state=FrontmatterState.UNREADABLE, problem=str(error), _fields={}
            )
            return unparsable
        readable: Frontmatter = cls(state=FrontmatterState.READABLE, problem="", _fields=fields)
        return readable

    def text(self, field_name: str) -> str:
        """A single-value field's value.

        Args:
            field_name: The field to read.

        Returns:
            The value, or an empty string when the field is absent.

        Raises:
            ValueError: If the field is a list, which only a caller's mistake asks for, since
                every field the manual defines has its shape checked when it's read.
        """
        # Refuse a list, which can't be read as one value
        field_value: FieldValue = self._fields.get(field_name, "")
        is_list: bool = (isinstance(field_value, tuple))
        if is_list:
            raise ValueError(f"{field_name} is a list; read it with items()")
        value: str = cast(str, field_value)
        return value

    def items(self, field_name: str) -> tuple[ListItem, ...]:
        """A list field's items.

        Args:
            field_name: The field to read.

        Returns:
            The items, or an empty tuple when the field is absent.

        Raises:
            ValueError: If the field is a single value, which only a caller's mistake asks
                for, since every field the manual defines has its shape checked when it's
                read.
        """
        # Refuse a single value, which has no items
        field_value: FieldValue = self._fields.get(field_name, ())
        is_single_value: bool = (isinstance(field_value, str))
        if is_single_value:
            raise ValueError(f"{field_name} is a single value; read it with text()")
        list_items: tuple[ListItem, ...] = cast(tuple[ListItem, ...], field_value)
        return list_items

    def is_filled(self, field_name: str) -> bool:
        """Whether a field is present and not empty.

        Args:
            field_name: The field to check.

        Returns:
            True when the field has a non-empty value or a non-empty list.
        """
        # An absent field counts as empty
        field_value: FieldValue = self._fields.get(field_name, "")
        is_filled: bool = (len(field_value) > 0)
        return is_filled

    def field_names(self) -> list[str]:
        """The names of every field, sorted.

        Returns:
            The field names.
        """
        # Sort the names, so callers report fields in a stable order
        names: list[str] = sorted(self._fields)
        return names


class _FieldLine(NamedTuple):
    """One `name: value` line of frontmatter.

    Attributes:
        name: The field's name.
        raw_value: The text after the colon, as written; may hold a comment.
    """

    name: str
    raw_value: str


class _FieldGroup(NamedTuple):
    """A top-level frontmatter field and the indented lines under it.

    Attributes:
        name: The field's name.
        raw_value: The text after the field's colon, as written.
        nested_lines: The indented lines below the field.
    """

    name: str
    raw_value: str
    nested_lines: tuple[str, ...]


def _block_lines(text: str) -> Optional[list[str]]:
    """Finds the lines of a note's frontmatter block.

    Args:
        text: A note's full contents, with Unix line endings.

    Returns:
        The lines between the opening and closing '---', or None when there's no block.

    Raises:
        FrontmatterError: If the block is opened but never closed.
    """
    # A note without an opening fence has no frontmatter
    FRONTMATTER_FENCE: str = "---"
    lines: list[str] = text.split("\n")
    has_opening_fence: bool = (lines[0].rstrip() == FRONTMATTER_FENCE)
    if not has_opening_fence:
        return None

    # Take everything up to the closing fence, looking from the line after the opening one
    FIRST_LINE_AFTER_OPENING_FENCE: int = 1
    line_index: int
    for line_index in range(FIRST_LINE_AFTER_OPENING_FENCE, len(lines)):
        is_closing_fence: bool = (lines[line_index].rstrip() == FRONTMATTER_FENCE)
        if is_closing_fence:
            block_lines: list[str] = lines[FIRST_LINE_AFTER_OPENING_FENCE:line_index]
            return block_lines
    raise FrontmatterError("frontmatter has no closing '---' line")


def _group_field_lines(lines: list[str]) -> list[_FieldGroup]:
    """Groups frontmatter lines into top-level fields and the indented lines under each.

    Args:
        lines: The frontmatter block's lines.

    Returns:
        Each field with its indented lines.

    Raises:
        FrontmatterError: If a line is neither a top-level field nor indented under one.
    """
    # Walk the lines, starting a group at each top-level field
    open_groups: list[tuple[_FieldLine, list[str]]] = []
    open_nested_lines: Optional[list[str]] = None
    line: str
    for line in lines:
        # Blank lines only space fields apart
        is_blank: bool = (line.strip() == "")
        if is_blank:
            continue

        # Start a new group at a top-level field
        is_indented: bool = (line.startswith(INDENTATION_CHARACTER))
        if not is_indented:
            open_nested_lines = []
            open_groups.append((_require_field_line(line), open_nested_lines))
            continue

        # Add an indented line to the group above it
        has_open_group: bool = (open_nested_lines is not None)
        if not has_open_group:
            raise FrontmatterError(
                f"can't read frontmatter line: {line.strip()}; {NOTE_FORMAT_HINT}"
            )
        cast(list[str], open_nested_lines).append(line)

    # Freeze each group
    field_groups: list[_FieldGroup] = []
    field_line: _FieldLine
    nested_lines: list[str]
    for field_line, nested_lines in open_groups:
        field_groups.append(_FieldGroup(
            name=field_line.name, raw_value=field_line.raw_value, nested_lines=tuple(nested_lines)
        ))
    return field_groups


def _parse_field_line(line: str) -> Optional[_FieldLine]:
    """Reads a `name: value` line.

    Args:
        line: One line of frontmatter, without leading indentation.

    Returns:
        The field, or None when the line isn't one.
    """
    # Match the line against the field shape
    FIELD_LINE_PATTERN: re.Pattern[str] = re.compile(
        r"(?P<name>[a-z][a-z-]*):(?:\s+(?P<value>.*))?$"
    )
    field_match: Optional[re.Match[str]] = FIELD_LINE_PATTERN.match(line)
    is_field: bool = (field_match is not None)
    if not is_field:
        return None

    # Split it into name and value
    matched_field: re.Match[str] = cast(re.Match[str], field_match)
    raw_value: str = (matched_field.group("value") or "")
    field_line: _FieldLine = _FieldLine(name=matched_field.group("name"), raw_value=raw_value)
    return field_line


def _require_field_line(line: str) -> _FieldLine:
    """Reads a line that must be a `name: value` field.

    Args:
        line: One line of frontmatter, without leading indentation.

    Returns:
        The field.

    Raises:
        FrontmatterError: If the line isn't a field.
    """
    # Reject a line that isn't a field
    field_line: Optional[_FieldLine] = _parse_field_line(line)
    is_field: bool = (field_line is not None)
    if not is_field:
        raise FrontmatterError(f"can't read frontmatter line: {line.strip()}; {NOTE_FORMAT_HINT}")
    required_field_line: _FieldLine = cast(_FieldLine, field_line)
    return required_field_line


def _parse_block(lines: list[str]) -> dict[str, FieldValue]:
    """Parses a frontmatter block's lines into fields.

    Args:
        lines: The frontmatter block's lines.

    Returns:
        Each field's value: a string, or a tuple of list items.

    Raises:
        FrontmatterError: If a line isn't in the note format, a field appears twice, or a
            field has anything but a list on the lines below it.
    """
    # Read each field as a one-line value, or as a list below an empty field
    fields: dict[str, FieldValue] = {}
    field_group: _FieldGroup
    for field_group in _group_field_lines(lines):
        is_repeated_field: bool = (field_group.name in fields)
        if is_repeated_field:
            raise FrontmatterError(f"{field_group.name} appears twice; merge them into one")
        inline_value: str = _parse_value(field_group.raw_value)
        has_nested_lines: bool = (len(field_group.nested_lines) > 0)
        if not has_nested_lines:
            fields[field_group.name] = inline_value
            continue

        # Only a list may sit below a field, and only below an empty one
        is_list_below: bool = (_is_item_marker_line(field_group.nested_lines[0]))
        is_empty_field: bool = (inline_value == "")
        is_list_field_shape: bool = (is_list_below and is_empty_field)
        if not is_list_field_shape:
            raise FrontmatterError(
                f"{field_group.name} continues onto the lines below it; write a value on "
                f"one line, or a list of '- ' items under an empty field; {NOTE_FORMAT_HINT}"
            )
        fields[field_group.name] = _parse_list_items(field_group.nested_lines)
    return fields


def _is_item_marker_line(line: str) -> bool:
    """Whether a line starts a list item: a hyphen followed by a space or nothing.

    Args:
        line: A line of frontmatter, with its indentation.

    Returns:
        True for a line whose first character after the indentation is a list item's hyphen.
    """
    # Match a hyphen that YAML reads as a list marker
    ITEM_MARKER_PATTERN: re.Pattern[str] = re.compile(r"-(?: |$)")
    is_marker_line: bool = (ITEM_MARKER_PATTERN.match(line.strip()) is not None)
    return is_marker_line


def _parse_value(raw_value: str) -> str:
    """Reads a one-line value, removing a trailing `# comment`.

    Args:
        raw_value: A value as written after its field's colon or its list item's hyphen.

    Returns:
        The value itself.

    Raises:
        FrontmatterError: If the value starts with YAML syntax, or holds a colon YAML would
            read as starting another field.
    """
    # A '#' after whitespace, or at the start, begins a comment
    COMMENT_PATTERN: re.Pattern[str] = re.compile(r"(?:^|\s)#.*$")
    value: str = COMMENT_PATTERN.sub("", raw_value.strip()).strip()

    # Reject a start YAML reads as syntax: an indicator character, or '-', '?', or ':' before
    # a space or the end
    YAML_SYNTAX_START_PATTERN: re.Pattern[str] = re.compile(
        r"""[\[\]{},&*!|>'"%@`]|[-?:](?:\s|$)"""
    )
    is_yaml_syntax_start: bool = (YAML_SYNTAX_START_PATTERN.match(value) is not None)
    if is_yaml_syntax_start:
        raise FrontmatterError(
            f"{value!r} starts with {value[0]!r}, which YAML reads as syntax rather than "
            "text; write the value plainly, without quotes, brackets, blocks, or markup at "
            f"its start; {NOTE_FORMAT_HINT}"
        )

    # Reject a colon followed by a space or the line's end, which YAML reads as a new field
    FIELD_COLON_PATTERN: re.Pattern[str] = re.compile(r":(?:\s|$)")
    has_field_colon: bool = (FIELD_COLON_PATTERN.search(value) is not None)
    if has_field_colon:
        raise FrontmatterError(
            f"{value!r} has a ':' followed by a space or the line's end, which YAML reads "
            "as starting another field; reword it"
        )
    return value


def _parse_list_items(nested_lines: tuple[str, ...]) -> tuple[ListItem, ...]:
    """Reads the list under a field.

    Args:
        nested_lines: The indented lines under the field; the first starts a list item.

    Returns:
        Each item, in order.

    Raises:
        FrontmatterError: If the lines don't form a list of readable items.
    """
    # Read each item's lines as one item
    items: list[ListItem] = []
    single_item_lines: list[str]
    for single_item_lines in _group_list_item_lines(nested_lines):
        items.append(_parse_list_item(single_item_lines))
    list_items: tuple[ListItem, ...] = tuple(items)
    return list_items


def _group_list_item_lines(nested_lines: tuple[str, ...]) -> list[list[str]]:
    """Splits the lines under a field into its list items' lines.

    Items start with '- ' at the list's indentation, set by the first line. An item's
    further lines line up under the text after its '- ', as YAML requires.

    Args:
        nested_lines: The indented lines under the field; the first starts a list item.

    Returns:
        Each item's lines, without indentation or the leading '- '.

    Raises:
        FrontmatterError: If an item's marker or further line isn't where the format puts it.
    """
    # Walk the lines, starting an item at each marker and continuing it on lined-up lines
    list_indentation: int = _indentation(nested_lines[0])
    continuation_indentation: int = (list_indentation + len(LIST_ITEM_MARKER))
    item_lines: list[list[str]] = []
    nested_line: str
    for nested_line in nested_lines:
        stripped_line: str = nested_line.strip()
        line_indentation: int = _indentation(nested_line)
        is_item_marker_line: bool = (_is_item_marker_line(nested_line))
        is_at_list_indentation: bool = (line_indentation == list_indentation)
        is_at_continuation_indentation: bool = (line_indentation == continuation_indentation)
        is_item_start: bool = (is_item_marker_line and is_at_list_indentation)
        is_continuation: bool = ((not is_item_marker_line) and is_at_continuation_indentation)

        # Start an item at its marker, whose text follows exactly one space
        if is_item_start:
            item_text: str = stripped_line[len(LIST_ITEM_MARKER):]
            has_extra_space: bool = (item_text.startswith(INDENTATION_CHARACTER))
            if has_extra_space:
                raise FrontmatterError(_list_line_problem(stripped_line))
            item_lines.append([item_text])
            continue

        # Reject anything else that isn't a lined-up further line of an item; an item is
        # always open here, since the first line can't be at the further lines' indentation
        if not is_continuation:
            raise FrontmatterError(_list_line_problem(stripped_line))
        item_lines[-1].append(stripped_line)
    return item_lines


def _indentation(line: str) -> int:
    """How far a line is indented.

    Args:
        line: A line of frontmatter.

    Returns:
        The number of indentation characters it starts with.
    """
    # Count what lstrip removes
    indentation_width: int = (len(line) - len(line.lstrip(INDENTATION_CHARACTER)))
    return indentation_width


def _list_line_problem(stripped_line: str) -> str:
    """Why a line under a list can't be read.

    Args:
        stripped_line: The line, without indentation.

    Returns:
        The problem, naming the line.
    """
    # Name the line and the rule it breaks
    problem: str = (
        f"can't read frontmatter line: {stripped_line}; list items line up under each "
        f"other, with no lists inside them; {NOTE_FORMAT_HINT}"
    )
    return problem


def _parse_list_item(item_lines: list[str]) -> ListItem:
    """Reads one list item: a plain value, or a small map of `name: value` lines.

    Args:
        item_lines: The item's lines, without indentation or the leading '- '; never empty.

    Returns:
        The plain value, or a read-only map of the item's fields.

    Raises:
        FrontmatterError: If the item is empty, a value isn't in the note format, a
            multi-line item has a line that isn't a field, or an item repeats a field.
    """
    # A single line that isn't a field is a plain value, which can't be empty
    first_field: Optional[_FieldLine] = _parse_field_line(item_lines[0])
    is_single_line: bool = (len(item_lines) == 1)
    is_first_line_a_field: bool = (first_field is not None)
    is_plain_value: bool = (is_single_line and (not is_first_line_a_field))
    if is_plain_value:
        plain_value: str = _parse_value(item_lines[0])
        is_empty_item: bool = (plain_value == "")
        if is_empty_item:
            raise FrontmatterError("a list item is empty; remove it or give it a value")
        return plain_value

    # Otherwise every line is a field of the item's map, each named once
    item_fields: dict[str, str] = {}
    item_line: str
    for item_line in item_lines:
        field_line: _FieldLine = _require_field_line(item_line)
        is_repeated_field: bool = (field_line.name in item_fields)
        if is_repeated_field:
            raise FrontmatterError(f"a list item has {field_line.name} twice; keep one")
        item_fields[field_line.name] = _parse_value(field_line.raw_value)
    item_map: Mapping[str, str] = MappingProxyType(item_fields)
    return item_map


def _with_empty_lists(fields: Mapping[str, FieldValue]) -> dict[str, FieldValue]:
    """Reads list fields written with nothing under them as empty lists.

    Args:
        fields: The parsed fields.

    Returns:
        A copy of the fields, with each empty list field as an empty tuple.
    """
    # Replace an empty value with an empty list, for list fields only
    normalized_fields: dict[str, FieldValue] = dict(fields)
    field_name: str
    for field_name in sorted(fields):
        is_list_field: bool = (field_name in LIST_FIELDS)
        is_empty_value: bool = (fields[field_name] == "")
        is_empty_list_field: bool = (is_list_field and is_empty_value)
        if is_empty_list_field:
            normalized_fields[field_name] = ()
    return normalized_fields


def _check_field_shapes(fields: Mapping[str, FieldValue]) -> None:
    """Checks the fields the manual defines have the shape it gives them.

    Args:
        fields: The parsed fields, with empty list fields already read as empty lists.

    Raises:
        FrontmatterError: If a list field holds a single value, or a single-value field
            holds a list.
    """
    # Compare each known field's shape with the manual's
    SINGLE_VALUE_FIELDS: frozenset[str] = frozenset(
        {"summary", "read-when", "depends-on", "status"}
    )
    field_name: str
    for field_name in sorted(fields):
        is_list: bool = (isinstance(fields[field_name], tuple))
        is_list_field: bool = (field_name in LIST_FIELDS)
        is_single_value_field: bool = (field_name in SINGLE_VALUE_FIELDS)
        is_list_field_with_value: bool = (is_list_field and (not is_list))
        if is_list_field_with_value:
            raise FrontmatterError(f"{field_name} must be a list")
        is_single_value_field_with_list: bool = (is_single_value_field and is_list)
        if is_single_value_field_with_list:
            raise FrontmatterError(f"{field_name} must be a single value, not a list")
