---
summary: Writes to the brain are gated by a permission prompt, owner-only commits, and a scan for brain damage, so unrelated work can't contaminate it.
read-when: About to change the brain, or wondering why editing it prompts for permission.
---

# 0006 Gated writes

## Context
Because the brain is always on, any session could write to it: an agent might save a note from
an unrelated task or record a wrong fact as true. The owner's main worry is contamination.

## Decision
Three layers, hardest first:
1. An `ask` permission rule on the brain's path makes every edit prompt the owner, enforced
   by Claude Code rather than by instructions.
2. Agents never commit to the brain. The owner reviews the diff and commits, which also catches
   writes made outside the file tools (for example through the shell).
3. `scan-for-brain-damage`, run before committing, flags files in unknown places and notes
   missing required fields (see 0016).

On top of these, the root README tells agents the brain is read-only during normal work.

## Alternatives rejected
- **Instructions only:** agents don't reliably follow them.
- **Deny all writes:** the brain must grow from real work, with approval.

## Consequences
Capturing knowledge costs one approval and one commit. Uncommitted junk is one `git restore`
away from gone.
