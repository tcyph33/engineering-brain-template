---
read-when: About to put code in a utils, helpers, common, shared, types, constants, or misc file or folder; a class keeps gaining methods; or new code has no obvious home.
---

# No dumping grounds

## In practice

A dumping ground is a file, folder, or class whose name says nothing about what's in it, so
anything can go there. Each one is hiding a concept nobody named:

| Dumping ground | The concept it's hiding |
|---|---|
| `utils/formatCurrency()` | money: `billing/money.ts` with `Money.format()` |
| `helpers/isWeekend()`, `addBusinessDays()` | a business calendar: `scheduling/business-calendar.ts` |
| `common/constants.ts` | each constant belongs to what it configures (`MAX_LINE_ITEMS` in `order.ts`) |
| `types.ts` with twenty interfaces | each type lives with what it describes, or is its own concept in its own file |
| `OrderService` with forty methods | the real things inside an order: line items, shipping, payment |

Where something goes:
1. **Name it.** What concept is it? If you can't name it, it isn't one thing yet.
2. **Find who uses it.** Put it in the nearest folder common to all of them.
3. **Name the file for it.**

The first file in a new `utils/` is the dangerous one: once the folder exists, everything
without a home lands there. The same goes for the first vague method on a class
(`handle`, `process`, `doStuff`).

## Tensions

- **Make the simplest change:** adding to `utils/` is the most direct change; naming the
  hidden concept is bigger, and it's the correct one. If the concept isn't in general domain
  knowledge or the project's `domain-concepts.md`, raise it rather than inventing it.
- **Model after real-world objects:** split god classes along the real things inside them,
  never into doer classes.
