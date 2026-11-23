---
read-when: Designing anything new, choosing between designs, letting a framework, ORM, or API shape decide how code is structured, or the language can't directly express a concept in the design.
---

# Design first, then express it in the language

## Explore designs before choosing one

The first design that works is rarely the simplest correct one. Before building anything
new, and before raising a new concept:

1. **Sketch at least two designs** that differ in their concepts or boundaries, not just in
   names.
2. **Check each against the principles:** real objects, domain words, how much someone must
   hold in their head, any special cases.
3. **Choose the simplest one that is conceptually correct**, and be able to say why each
   other one lost.
4. **Show the user the options** when they're close, or when the choice is hard to reverse.

Design until the remaining choices are routine, then stop.

## Then express it in the language

Once the design is chosen, choose how the language and framework express it. The tools
serve the design; they don't decide it.

| Shaped by the tools | Design first |
|---|---|
| one class per ORM table, with the logic in services | the domain model first; the ORM maps it to storage |
| the framework's scaffold decides the folders | domain folders; framework plumbing only where it's required |
| the language has no enums, so status is a string compared everywhere | an `InvoiceStatus` type built once and used everywhere |
| an external API's JSON shape used as the core model | the model has the domain's shape; it's mapped to and from the API at the edge |

When the language can't express a concept directly, build the missing piece once, in one
place, rather than working around the gap at every use.

Design first doesn't mean fighting the language. Use its idioms (naming conventions, error
handling, file layout) to express the design; just don't let them decide it.

## Tensions

- **Make the simplest change:** in existing code, the design already exists. Express the
  change in it rather than redesigning. If that design was shaped by the tools rather than
  the domain, raise the redesign as its own change.
