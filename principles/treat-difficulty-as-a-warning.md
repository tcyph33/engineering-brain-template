---
read-when: Something is hard to name, hard to test, or needs a long comment to explain; it keeps needing special cases; or a change keeps fighting the code.
---

# Treat difficulty as a design warning

## In practice

Common kinds of difficulty, and the design problem each usually points at:

| Difficulty | What it usually means |
|---|---|
| hard to name | it does more than one thing, or it's a concept nobody has named yet |
| hard to test | it depends on too much, or hides its inputs (global state, the clock, the network) |
| needs a long comment to explain | the names or structure don't express the concept |
| keeps needing special cases | a concept is wrong or missing; the cases are trying to be it |
| a small change touches many files | one concept is spread out instead of living in one place |

These are examples, not the whole list. Whenever the code keeps fighting you, ask what about
its design makes this hard.

When you hit one:
1. **Stop pushing through.** A workaround hides the signal and adds entropy.
2. **Name the design problem.**
3. **Fix it if the fix is within the change.** If it needs a new concept or a restructuring
   beyond the change, raise it: say what's hard and what you think is wrong or missing.

Not every difficulty is a design problem. An unfamiliar library, a hard algorithm, or a
domain rule that really is complicated can be hard in well-designed code. Ask whether the
difficulty is in the problem itself or in how the code is shaped.

## Tensions

- **Make the simplest change:** pushing through is often the most direct change, and fixing
  the design is bigger. Fix what's within the change; raise the rest.
