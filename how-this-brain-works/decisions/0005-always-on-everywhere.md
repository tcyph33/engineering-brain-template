---
summary: The brain loads automatically in every Claude Code session, via an import in the user-level ~/.claude/CLAUDE.md.
read-when: Setting up the brain on a machine, or considering making it load only on request or only in some folders.
---

# 0005 Always on everywhere

## Context
Most bad changes happen on work that doesn't feel big enough to bring in extra context. A
brain that loads only when invoked would be missing exactly then. And engineering work isn't
only done inside a repo: conversations about design or a project often start elsewhere.

## Decision
The user-level `~/.claude/CLAUDE.md` imports the brain's root README, so every session gets
the brain and no repo ever mentions it. The root README imports the other always-loaded
files, so the brain controls what is always loaded.

## Alternatives rejected
- **A `CLAUDE.md` in the folder that holds the code repos:** the first version of this
  decision. It kept the brain out of unrelated sessions, but it misses conversations that use
  the brain without being in a repo, and repos cloned elsewhere. Keeping the brain from
  coloring other work wasn't a real benefit: coloring the work is the point, so the principles
  never have to be re-taught.
- **Invoke only for a story or issue:** misses the "small" changes where over-engineering
  happens. A human doesn't switch their knowledge on only for tickets.
- **An instruction to "go read the brain":** loading should not depend on the agent choosing to.

## Consequences
The always-loaded files cost context in every session, including ones unrelated to
engineering, so they have a size budget (see 0007). Setup is a step on each machine and must
be documented clearly.
