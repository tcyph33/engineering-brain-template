---
summary: Notes are plain markdown with relative links and YAML frontmatter, in a git repo; no Obsidian-specific syntax.
read-when: Choosing link syntax or formatting for a note, or considering a note-taking app.
---

# 0015 Plain markdown

## Context
The brain is read by agents, by GitHub, by the owner, and later by its own lint. A note-taking
app like Obsidian was considered.

## Decision
A git repo of plain markdown: standard relative links, YAML frontmatter, no plugin syntax.
Git provides history, backup, sync, and privacy.

## Alternatives rejected
- **Obsidian now:** not needed. Because the brain is plain markdown, it can be opened as an
  Obsidian vault any time later.
- **Wikilinks:** resolve by file name, and this brain has many files with the same name
  (`README.md`, `lessons-learned/`).
- **Plugin syntax (for example Dataview queries):** only works inside the app; elsewhere it's
  raw query text instead of knowledge.

## Consequences
None beyond the rules themselves.
