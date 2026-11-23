"""note_with_frontmatter: the text of a note whose frontmatter holds the given lines."""

from __future__ import annotations


def note_with_frontmatter(*frontmatter_lines: str) -> str:
    """A note whose frontmatter block holds the given lines, followed by a short body.

    Args:
        frontmatter_lines: The lines between the '---' fences.

    Returns:
        The note's full text.
    """
    # Wrap the lines in fences and add a body
    note_text: str = "---\n" + "\n".join(frontmatter_lines) + "\n---\n# Note\n"
    return note_text
