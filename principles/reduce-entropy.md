---
read-when: Any change to existing code, especially one that seems too small to matter (an added condition, option, or flag, or a copied-and-tweaked function).
---

# Strive to reduce entropy

## In practice

Big changes get designed and reviewed, so they rarely break a system's concepts. Small ones
do: one extra condition, one copied function, one "temporary" flag, each reasonable on its
own. None of them looks like a design decision, so none gets checked as one. The smaller a
change looks, the more deliberately it gets checked against the system's concepts: no special
cases, no second way of doing something that already has a way, no concept that doesn't fit.

The test, for every change: explain the system before and after. If the explanation gained
an "except when…" or an "or, alternatively…", the change added entropy.

| Adds entropy | Keeps integrity |
|---|---|
| `if (customer.id === "acme")` | model the rule Acme follows (`customer.paymentTerms`) and give it to Acme |
| a second HTTP client next to the existing one | use the existing one, or replace it everywhere as its own change |
| copying a function and tweaking the copy | change the original so its concept covers both cases |
| a field whose meaning depends on another field | two fields, one per concept |

"Reduce," not just "don't add": when the change touches a special case or a second way, and
removing it is within the change, remove it. Delete code the change makes dead.

## Tensions

- **Simplest change:** a special case is often the smallest diff. Fitting the existing
  concepts can be a larger change, and that larger change is the simpler one.
- **Scope:** reducing entropy beyond what the change touches grows the change. Clean up what
  you touch; raise the rest as its own change.
- **Isolate what's known to change:** a new abstraction is itself a new concept. Add one only
  for volatility with evidence.
