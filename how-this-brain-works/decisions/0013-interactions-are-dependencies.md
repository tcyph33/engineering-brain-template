---
summary: How projects interact is recorded as dependency notes on the consumer side, with consumers derived from depends-on, whoever owns the provider.
read-when: Recording how one project uses another or an external system.
---

# 0013 Interactions are dependencies

## Context
Projects interact. An interaction isn't a thing of its own but a relationship, and an engineer
knows it from inside each project: what my project relies on, and (found when needed) who relies
on mine. Knowing who consumes a thing is exactly what prevents breaking or over-guarding it.

## Decision
Each project's `dependencies/` holds one note per thing it relies on, other teams' systems and
the owner's own projects alike. The note holds the consumer's side: what it's used for, what we
rely on (each assumption marked confirmed or unconfirmed), quirks, and who owns it, pointing at
the provider's published contract. `depends-on` names the provider, and grouping notes by it
gives each provider's consumers within the brain. Consumers outside the brain are listed in the
provider's README under "Who relies on this." The rule is the same whoever owns the provider;
for the owner's own projects, their brain notes only add context (direction, tenets).

## Alternatives rejected
- **A `project-interactions/` folder:** felt forced, and its file names would combine projects
  and flows as it grew.
- **Hand-written consumer lists in each provider:** drift.
- **Letting the owner's own projects depend on each other's internals:** couples them; a missing
  published contract is a gap to fix, not a reason to point at internals.

## Consequences
The owner's own projects often lack formal contracts; pointers go to whatever acts as one,
marked `informal contract`.

"Found when needed" is a step in the root README, not left to memory: before changing anything
another project could use, search `depends-on` for its consumers. A provider's own notes never
name its consumers, so nothing else would send an agent to them.
