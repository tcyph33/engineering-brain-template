---
summary: Folders have no index; agents find notes by scanning their frontmatter, and projects are found by their repos list.
read-when: Tempted to add a list of notes or projects to a README.
---

# 0008 Scan notes instead of indexes

## Context
An index in a folder's README repeats each note's summary and cue, so it drifts unless a
generator keeps it current. A repo-to-project map in the root README would grow with every
project and sit in the always-loaded layer.

## Decision
No indexes. Folder READMEs say only what belongs and what doesn't. Agents scan note
frontmatter (`summary`, `read-when`) directly, which is always current. Each project's README
lists its repos in frontmatter, and the current project is found by searching those lists.
The two always-loaded READMEs hold the principles and skill entries themselves, not copies.

## Alternatives rejected
- **Hand-maintained indexes:** drift.
- **Generated indexes:** need a generator and still duplicate the notes.
- **Project list and repo map in the root README:** grows forever in the always-loaded layer
  and changes with every new project.

## Consequences
Finding things takes a scan instead of one read, which is a single cheap command.
