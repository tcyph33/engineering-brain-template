---
summary: The brain knows about repos and skills; repos and skills never know about the brain.
read-when: Tempted to make a skill read the brain, or to add a reference to the brain inside a code repo.
---

# 0002 One-way dependency

## Context
The system has three parts: the brain (knowledge), the toolkit (skills: procedures), and the
code repos the work happens in. Repos are often owned by other teams. Skills are useful on
their own, outside any brain.

## Decision
Dependency runs one way. The brain names skills (`when-to-use-skills/`) and points at repos.
Skills never reference the brain; they are procedures whose steps ask questions, and the
agent answers them from what it knows, which includes the brain. Repos never reference the
brain, just as they don't know a human's brain exists. The brain is a separate repo of
content only; the skills live in the toolkit repo.

## Alternatives rejected
- **Brain as a skill:** the brain is content, like a database is not the code that queries
  it. A skill also only runs when invoked, and missing context is the very problem.
- **Each repo's CLAUDE.md pointing into the brain:** breaks for repos owned by others and
  couples every repo to one person's tool.
- **A check inside repos' PRs that flags changes to things the brain references:** the brain
  doesn't own those repos, so it can't ask them to know about it.
- **Brain-upkeep skills (lint, init) in the toolkit that know the brain's format:** breaks the
  one-way rule; the brain maintains itself instead (see 0016).

## Consequences
Skills work with or without a brain; with one they work better. The brain must be loaded by
the user's own configuration, not by anything in a repo or skill (see 0005).
