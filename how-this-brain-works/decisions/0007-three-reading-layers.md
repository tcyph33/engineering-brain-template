---
summary: Knowledge is always loaded, recalled for the task, or looked up, and the always-loaded layer has a size budget.
read-when: Deciding whether something should be always loaded, or when the always-loaded files grow.
---

# 0007 Three reading layers

## Context
An agent can't hold the whole brain in context, and a human doesn't either: they have a
sense of who they are and what they know, recall what's relevant to the task, and look up
details.

## Decision
- **Always in mind:** the root README, `principles/README.md`, `when-to-use-skills/README.md`.
  Judgment and tool habits apply to everything, so they can't depend on recall.
- **Recalled for the task:** the project's README and domain concepts, lesson summaries, and
  the dependency notes a change touches.
- **Looked up:** a note's full text and its pointers, only when a decision depends on it.

The always-loaded files together stay under about 150 lines.

## Alternatives rejected
- **Load everything:** wastes context and buries the principles.
- **Load nothing until asked:** misses the moments the knowledge matters (see 0005).

## Consequences
Recall depends on the agent noticing it needs something. `read-when` cues make that easier,
and well-made skills that ask the right questions help further, but it isn't enforced.
