---
summary: The brain models an experienced engineer's memory, holding the gist and the why, not documentation.
read-when: Deciding whether something belongs in the brain at all, or how much detail a note should hold.
---

# 0001 Mimic an engineer's memory

## Context
Agents introduce bugs and bloat mostly by not understanding the whole system: they see one
repo, not who consumes what or what the product is for, so they don't keep conceptual
integrity. Many fixes for this add process machinery. The owner wanted the agent to work the
way a good human engineer does, since that tends to produce the best results.

## Decision
The brain mimics how an experienced engineer's memory works: remember the gist and the why,
know where the details live, and re-check details before acting on them. It holds only what
the code can't tell you. The test for any note: would a new senior hire need someone to tell
them this?

## Alternatives rejected
- **Perfect recall (copy everything in):** goes stale and starts lying, the way a human's
  memory of a document goes stale when the document changes.
- **Pointers only, no gist:** the agent would have to rediscover the system each time, and
  dangling pointers would leave it with nothing.
- **Machinery-heavy approaches** that add process to make up for missing context: they treat
  the symptom.

## Consequences
Some duplication exists, but only as gist, pitched at a level that rarely changes. Details
are verified on use. Content quality sets the ceiling on how much the brain helps.
