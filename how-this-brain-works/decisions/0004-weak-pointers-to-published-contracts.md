---
summary: Pointers are weak references to what providers publish, recorded with identity, verified before use, and repaired by proposal.
read-when: Writing a pointer, finding a broken one, or deciding what in another system a note may point at.
---

# 0004 Weak pointers to published contracts

## Context
The brain can't hold everything, so it points at code and docs. Pointers dangle when targets
move or are deleted, and the brain doesn't own most targets, so it can't keep them alive or
be told when they change.

## Decision
Pointers are weak references, like `weak_ptr`: non-owning and checked before use. They point
only at what a provider publishes (API specs, schemas, contracts, public docs), regardless of
who owns the provider. Each one records what the target is, where it lives (never line
numbers), and when it was last verified. A broken pointer is repaired by searching for the
target by identity and proposing the new location for the owner to confirm; the note is
quarantined (`status: unverified`) until then.

## Alternatives rejected
- **Line-number or internal-file pointers:** break on almost any refactor.
- **Owning references (`shared_ptr`) or prevention inside repos:** the brain doesn't own other
  teams' repos and repos don't know the brain exists (see 0002).
- **Silent automatic re-pointing:** a pointer that resolves to the wrong thing is worse than a
  broken one.
- **Pointing at internals of the owner's own projects from other projects:** couples the
  owner's projects to each other's internals (see 0013).

## Consequences
Published interfaces move rarely and usually with notice, so pointers stay valid longer.
Staleness is detected rather than silently trusted: the brain scan flags pointers whose
targets are gone or changed since `verified` (see 0016).
