---
summary: Decision records for a project live in the repo they're about; the brain points at them.
read-when: Recording why a design choice was made in a project.
---

# 0012 Decisions live in repos

## Context
Decision records ("why is it this way, and what was rejected") are valuable to everyone who
works in a repo, not only to the agent.

## Decision
Project decision records live in the repo they're about, following that repo's conventions.
Decisions spanning several repos go in the repo that owns the concern. The brain points at them,
for example from a design tenet's why. The brain's own decisions live here, in the brain's
repo, by the same rule.

## Alternatives rejected
- **A `decisions/` folder in each project in the brain:** hides them from everyone outside the
  brain, and duplicates any records the repo already keeps.

## Consequences
Writing decision records becomes part of the process skills, which must keep the same bar:
significant decisions only, or repos fill with trivial records.
