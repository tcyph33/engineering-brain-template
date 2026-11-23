---
summary: Each brain is a self-contained private repo; a new brain starts from the public template, which holds the framework and a starter set of principles and skill entries.
read-when: Starting a new brain, or tempted to share content between brains.
---

# 0003 Self-contained brains

## Context
A person may keep more than one brain, each covering all of its projects like a single
memory. Engineering judgment should carry over to a new brain; project knowledge must stay in
the brain it belongs to. Brains are private, so a new one can't start as a copy of someone
else's.

## Decision
Each brain is a single, self-contained private repo. A new brain starts from the public
[engineering-brain-template](https://github.com/tcyph33/engineering-brain-template): the manual
and decision records, the folder READMEs, and a starter set of principles and skill entries.
It has no projects and no lessons; those are the owner's own. The owner can then change
anything, principles included. A brain doesn't know any other brain exists.

## Alternatives rejected
- **Copying an existing brain minus its projects (the first version of this decision):**
  brains are private, so others can't copy one, and a copy carries the old brain's lessons
  and a git history that contains its projects.
- **The template as a folder in the toolkit, with a copy script:** mixes a brain's structure
  into a toolbox of procedures, and a copy script adds files but never removes old ones.
- **Keeping brains in sync with the template through a git remote:** overkill while the
  template has one maintainer; it can be added later.
- **One brain per project:** a human has one memory that knows many systems.
- **A shared core brain plus separate domain brains:** the agent must merge two indexes,
  every note needs a which-repo decision, and links cross repo boundaries.
- **Labeling brains by kind:** unnecessary; a brain is just "the brain".

## Consequences
A brain made from the template doesn't receive later template changes. Whoever maintains the
template makes each framework change (anything outside `projects/` and the notes in
`lessons-learned/`) in both the template and their own brain.
