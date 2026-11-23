---
summary: A project holds a README (purpose, tenets, build, consumers, direction), domain-concepts.md, dependencies/, and lessons-learned/, and nothing that code or repos already hold.
read-when: Adding a project, or tempted to add a new file or folder to a project.
---

# 0011 Project knowledge shape

## Context
Conceptual integrity depends on knowing what a project is for, the few design ideas it's built
on, and which constraints are real. Code shows structure but rarely the why. Anything the brain
holds that code also holds goes stale.

## Decision
Every project has:
- `README.md`: what it's for, design tenets (at most about seven, each with why and what would
  violate it), how it's built, who relies on it from outside the brain, and direction (dated).
- `domain-concepts.md`, always present: only where the project's model of its domain differs
  from general knowledge. If empty, it says so on purpose.
- `dependencies/` and `lessons-learned/`.

The brain holds what's needed to judge whether a change fits; design docs hold what's needed to
build it.

## Alternatives rejected
- **`repos/` notes per repo:** for owned repos the code is readable directly, so these restate
  code. Each repo's role is one line in "How it's built."
- **A `design-concepts/` folder:** started doing the design doc's job.
- **A top-level `domain-knowledge/` folder:** general domain knowledge is already broad; what's
  missing is project-specific.
- **Domain concepts as a README section in some projects and a file in others:** inconsistent.
- **A `projects/README.md` landscape:** low value when projects are genuinely separate;
  interactions are covered by dependencies, and cross-project rules go in the shared provider's
  tenets. Add one only if several projects become one system.
- **A project `decisions/` folder:** decision records belong in repos (see 0012).

## Consequences
Seeding a project is mostly an interview about purpose, tenets, and domain differences. Only
the owner can supply those.
