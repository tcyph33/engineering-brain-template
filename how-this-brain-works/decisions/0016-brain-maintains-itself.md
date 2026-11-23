---
summary: The brain checks itself with the scan-for-brain-damage tool, which lives inside the brain, runs every check by default, and is run before committing.
read-when: Building or changing tooling that checks or maintains the brain.
---

# 0016 The brain maintains itself

## Context
Pointers rot, notes go stale, and files land in the wrong place. Checking these requires
knowing the brain's format, but skills must not know about the brain (see 0002).

## Decision
The brain's upkeep tooling lives in `how-this-brain-works/`, next to the manual that defines
the format it checks, the way a brain's own upkeep is part of the brain. A brain made from
the template gets its upkeep with it.

`scan-for-brain-damage/` checks every rule in the manual that a script can, including
pointers against GitHub. Every check runs by default and is opted out of explicitly
(`--skip-pointers`), so nothing is skipped by forgetting to turn it on. It uses only Python's
standard library, so any brain can run it without installing anything. It's run before
committing. It's a folder of small modules, one per concept and one per kind of damage, so
the code follows the same principles it helps the brain keep.

It reads frontmatter in exactly the shape the manual's note format shows and rejects the
rest of YAML, so the scan and GitHub never read a note differently, and the reader stays
small. It ships with its tests in `tests/`: each builds a small brain in a temporary folder
that's removed afterward, and tests marked as calling the real GitHub are skipped when `gh`
can't be used.

## Alternatives rejected
- **A lint skill in the toolkit:** would have to know the brain's structure, breaking the
  one-way dependency.
- **"Lint" as its name:** says how it works, not what it's for.
- **One script file:** it held a dozen concepts in one long file, against the principle that
  a file holds one main thing named for it.
- **A top-level folder for the scan:** the brain's top level holds knowledge; tooling there
  would mix the two and add a row to the always-loaded README.
- **Reading every form YAML allows:** quotes, flow lists, and block values each needed
  their own parsing, which is where most of the scan's bugs were; notes only need one shape.
- **An LLM doing the checks:** it can miss or invent damage from one run to the next, while
  a script gives the same answer every time. An LLM fits the rules a script can't judge.
- **Checks that must be turned on:** a check that has to be remembered gets forgotten.
- **A pre-commit hook:** not yet; it adds a setup step. Add it if the scan gets skipped.
- **Listing consumers by `depends-on`:** the root README's consumer check already finds them
  with one search.
- **Comparing framework files with the template:** only the template's maintainer needs it,
  and it can't run by default without knowing where the template is.

## Consequences
When a rule in the manual changes, its check in the scan and that check's tests change with
it. Rules a script can't judge (one idea per note, stating the why) still rely on the
owner's review.
