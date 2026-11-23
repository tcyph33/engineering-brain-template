---
read-when: Naming or shaping anything (a class, function, variable, table, API, or doc), or when a concept you need has no name in the domain.
---

# Build in terms of the domain, not the solution

## In practice

Solution words such as `data`, `item`, `record`, `entry`, `payload`, `info`, and `flag`
describe the mechanism, and almost always stand in for a domain word that already exists.

| Instead of | Write |
|---|---|
| `filteredItems` | `overdueInvoices` |
| `UserDataManager.processRecords()` | `membership.renew()` |
| an `entries` table with a `type` column | `invoices` and `payments` tables |
| `POST /api/process-data` | `POST /invoices/{id}/payments` |

The test: could someone who knows the domain, but not the code, say what each name means?
Docs and comments pass the same test: "finds every invoice past its due date," not "loops
over the records."

Even mechanics carry the domain they work on: a loop index over emails is `emailIndex`, not
`i`. When the code's own domain is technical, that is the domain: a JSON parser's concepts
are tokens and values.

## Never invent a domain concept

Domain concepts come from general knowledge of the domain, the project's
`domain-concepts.md`, or the user. Never from what the code needs to compile.

You're inventing one when:
- the name is a noun nobody in the domain says, or needs a comment to explain;
- it fuses two real concepts into one (`OrderInvoice`);
- it reuses a domain word for something that word doesn't mean in the domain;
- it exists only to make the code work, but appears in the model as if it were real.

Then stop and raise it: say what's missing, which domain term might fit, and why the existing
concepts don't cover it. Don't proceed under a placeholder name; it becomes permanent.

## Tensions

- **Reduce entropy:** if existing code already uses a solution name, adding the right name
  beside it gives one concept two words. Follow the existing name in the change and raise
  the rename as its own change.
- **Design first, then express it in the language:** framework vocabulary (`Controller`,
  `Handler`) stays in the plumbing; see
  [model after real-world objects](model-after-real-world-objects.md).
