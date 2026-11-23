---
summary: Principles are unranked one-liners with their why, weighed by situation, each with a file on how to apply it; design preferences live with them for now.
read-when: Adding or changing a principle, or when two principles seem to conflict.
---

# 0009 Unranked principles

## Context
Principles are the owner's engineering judgment and apply to every change, so they are always
loaded. They sometimes pull against each other.

## Decision
`principles/README.md` holds each principle as a bold imperative plus a one-line why.
They are not ranked: which weighs more depends on the situation, and conflicts that change a
design get raised with the owner. Design preferences (how APIs, data, and errors should be
shaped) live in `principles/` too. Every principle has a `<name>.md` on how to apply it
(examples, tensions with other principles, exceptions), whose frontmatter has only
`read-when`, since the README line is its summary. Only the owner adds or
changes principles. Similar principles that are not the same stay separate.

## Alternatives rejected
- **Priority order:** which principle applies more depends on the situation, not a fixed order.
- **A file only for principles that need more (the first version of this decision):** a
  one-liner says what's valued but not what a violation looks like in a diff, so every
  principle needs examples; and "some have a file" is a judgment call each time.
- **A separate `design-preferences/` folder:** the line between the two was the fuzziest in the
  layout. Split them only if the always-loaded budget gets tight.
- **Merging similar principles** (for example "reduce entropy" and "simplest change that fits
  existing concepts"): they overlap but aren't the same, and the tension between them is useful.

## Consequences
Principles must be specific enough to judge a diff against, or they read well and change
nothing.
