---
summary: The brain's own checks (lint, pointer verification, consumer lists) live inside the brain, not in the toolkit.
read-when: Building or changing tooling that checks or maintains the brain.
---

# 0016 The brain maintains itself

## Context
Pointers rot, notes go stale, and files land in the wrong place. Checking these requires
knowing the brain's format, but skills must not know about the brain (see 0002).

## Decision
The brain's upkeep tooling lives in `how-this-brain-works/`, next to the manual that defines
the format it checks, the way a brain's own upkeep is part of the brain. A brain made from
the template gets its upkeep with it.

## Alternatives rejected
- **A lint skill in the toolkit:** would have to know the brain's structure, breaking the
  one-way dependency.

## Consequences
Not built yet; until then, the checks are manual. A new brain starts from the public template
(see 0003), so the upkeep tooling ships in it.
