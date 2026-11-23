"""NoteKind: the kinds of markdown file the manual defines, where each lives, and the
frontmatter each requires. This is the manual's layout, as the scan understands it."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, cast

# How the manual names files: lowercase words joined by hyphens.
KEBAB_NAME_PATTERN: str = r"[a-z0-9-]+"
# Where lessons live: the brain's own lessons-learned/ folder, or a project's.
LESSONS_FOLDER_PATTERN: str = rf"(projects/{KEBAB_NAME_PATTERN}/)?lessons-learned"


class FrontmatterRule(Enum):
    """What a kind of note allows in its frontmatter."""

    NONE = "has no frontmatter"
    ONLY_REQUIRED = "has only its required fields"
    REQUIRED_AND_OPTIONAL = "has its required fields and may have optional ones"


@dataclass(frozen=True)
class NoteKind:
    """A kind of markdown file the manual defines, and the frontmatter it requires.

    Attributes:
        name: What the manual calls this kind of file.
        path_pattern: The pattern a brain-relative path must fully match; a kind whose
            files are numbered captures the number in a group named "number".
        required_fields: Frontmatter fields every file of this kind must fill in.
        frontmatter_rule: What else this kind allows in its frontmatter.
    """

    name: str
    path_pattern: re.Pattern[str]
    required_fields: frozenset[str]
    frontmatter_rule: FrontmatterRule

    @classmethod
    def of(cls, path: str) -> Optional[NoteKind]:
        """Finds which kind of note the manual says a path is.

        Args:
            path: Any brain-relative path.

        Returns:
            The matching kind, or None when the manual defines no such markdown file.
        """
        # Return the first kind whose pattern the path matches
        kind: NoteKind
        for kind in NOTE_KINDS:
            is_match: bool = (kind.path_pattern.fullmatch(path) is not None)
            if is_match:
                return kind
        return None

    def number_in(self, path: str) -> Optional[str]:
        """The number in a numbered file's name, such as a decision record's.

        Args:
            path: A brain-relative path.

        Returns:
            The number, or None when the path isn't a numbered file of this kind.
        """
        # Read the number group when the path is this kind of file
        NUMBER_GROUP: str = "number"
        path_match: Optional[re.Match[str]] = self.path_pattern.fullmatch(path)
        is_match: bool = (path_match is not None)
        has_number_group: bool = (NUMBER_GROUP in self.path_pattern.groupindex)
        is_numbered_file: bool = (is_match and has_number_group)
        if not is_numbered_file:
            return None
        number: str = cast(re.Match[str], path_match).group(NUMBER_GROUP)
        return number


# The kinds other parts of the scan single out by name.
DECISION_KIND: NoteKind = NoteKind(
    name="decision record",
    path_pattern=re.compile(
        rf"how-this-brain-works/decisions/(?P<number>\d{{4}})-{KEBAB_NAME_PATTERN}\.md"
    ),
    required_fields=frozenset({"summary", "read-when"}),
    frontmatter_rule=FrontmatterRule.REQUIRED_AND_OPTIONAL,
)
PRINCIPLE_FILE_KIND: NoteKind = NoteKind(
    name="principle file",
    path_pattern=re.compile(rf"principles/{KEBAB_NAME_PATTERN}\.md"),
    required_fields=frozenset({"read-when"}),
    frontmatter_rule=FrontmatterRule.ONLY_REQUIRED,
)
LESSON_KIND: NoteKind = NoteKind(
    name="lesson",
    path_pattern=re.compile(
        rf"{LESSONS_FOLDER_PATTERN}/{KEBAB_NAME_PATTERN}\.md"
    ),
    required_fields=frozenset({"summary", "read-when", "occurrences"}),
    frontmatter_rule=FrontmatterRule.REQUIRED_AND_OPTIONAL,
)

# Every kind of markdown file the manual defines. A path matching none of them is in the
# wrong place, or has a name the manual doesn't allow (names are kebab-case).
NOTE_KINDS: tuple[NoteKind, ...] = (
    NoteKind(
        name="root README",
        path_pattern=re.compile(r"README\.md"),
        required_fields=frozenset(),
        frontmatter_rule=FrontmatterRule.NONE,
    ),
    NoteKind(
        name="folder README",
        path_pattern=re.compile(
            r"(principles|when-to-use-skills|lessons-learned|projects"
            r"|how-this-brain-works/decisions)/README\.md"
        ),
        required_fields=frozenset(),
        frontmatter_rule=FrontmatterRule.NONE,
    ),
    NoteKind(
        name="manual",
        path_pattern=re.compile(r"how-this-brain-works/README\.md"),
        required_fields=frozenset(),
        frontmatter_rule=FrontmatterRule.NONE,
    ),
    DECISION_KIND,
    PRINCIPLE_FILE_KIND,
    NoteKind(
        name="skill entry file",
        path_pattern=re.compile(rf"when-to-use-skills/{KEBAB_NAME_PATTERN}\.md"),
        required_fields=frozenset({"read-when"}),
        frontmatter_rule=FrontmatterRule.ONLY_REQUIRED,
    ),
    LESSON_KIND,
    NoteKind(
        name="project README",
        path_pattern=re.compile(rf"projects/{KEBAB_NAME_PATTERN}/README\.md"),
        required_fields=frozenset({"summary", "repos"}),
        frontmatter_rule=FrontmatterRule.REQUIRED_AND_OPTIONAL,
    ),
    NoteKind(
        name="domain concepts",
        path_pattern=re.compile(rf"projects/{KEBAB_NAME_PATTERN}/domain-concepts\.md"),
        required_fields=frozenset({"summary", "read-when"}),
        frontmatter_rule=FrontmatterRule.REQUIRED_AND_OPTIONAL,
    ),
    NoteKind(
        name="dependency note",
        path_pattern=re.compile(
            rf"projects/{KEBAB_NAME_PATTERN}/dependencies/{KEBAB_NAME_PATTERN}\.md"
        ),
        required_fields=frozenset({"summary", "read-when", "depends-on"}),
        frontmatter_rule=FrontmatterRule.REQUIRED_AND_OPTIONAL,
    ),
)
