---
read-when: Choosing between designs, deciding the boundary or interface between parts, or a change requires understanding many parts at once.
---

# Keep the complexity anyone must hold in their head small

## In practice

The test: to change this part safely, what else must you know? Other files, hidden rules,
the order things must happen in, shared state. The less, the better.

| Must hold in your head | Instead |
|---|---|
| amounts are in cents, except on refunds | a `Money` type that carries its own unit |
| call `connect()` before `send()` | `send()` works on its own, or nothing unconnected can be created |
| `status === 3` means archived | `invoice.isArchived()` |
| a global config read in a dozen places | the setting passed to the part that needs it |

What keeps it small:
- **Hide how a part works.** Callers use what it does and never need to know how.
- **Enforce rules inside the part.** An invoice that can't have a negative total, rather than
  every caller remembering not to make one.
- **Make dependencies explicit and one-way.** Inputs come in as arguments, not from global
  state or setup done somewhere else first.

Complexity is about what must be understood at once, not how much code there is. Ten small
files that can each be read alone are simpler than one file whose parts all depend on each
other.

## Tensions

- **Isolate what's known to change:** an abstraction shrinks what you must know about the
  volatile part, but it is one more thing to understand. Worth it only with evidence that
  the part will change.
