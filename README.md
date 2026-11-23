# Software Engineering Brain

This is your engineering memory: how to build software well, and what you know about each
project. Treat it like memory, not documentation. It holds the gist and the "why"; details
live in code and published docs. Verify details before relying on them.

## How to use it

1. Principles and skill usage below are always in mind. Apply them to everything.
2. Find the project you're working in: search the `repos:` lists in `projects/*/README.md`
   for the current repo, then read that project's README.md before changing anything.
3. Scan the summaries and cues of the lessons in `lessons-learned/` and the project's
   `lessons-learned/`; open a lesson when its cue matches your task.
4. Before a note drives a decision, follow its pointers and confirm they still hold.
5. Before changing anything another project could use, find its consumers: search for
   `depends-on: <this project's folder>` in `projects/*/dependencies/` and read each match.

## Rules

1. If the brain doesn't cover something you needed, say so plainly. Don't fill the gap with
   a guess. Note the gap so it can be captured when the work is done.
2. If the brain and the code disagree on a fact, the code wins: flag the note as stale.
   If they disagree on intent ("why it's this way"), stop and ask.
3. This brain is read-only during normal work. Propose changes; never make them silently.
   Read `how-this-brain-works/` before proposing any change.

## What's here

| Folder | What it holds | Open when |
|---|---|---|
| `principles/` | How you decide what to build and how | Always loaded |
| `when-to-use-skills/` | When you reach for each skill | Always loaded |
| `lessons-learned/` | Mistakes made before and what to do instead, across projects | A lesson's cue matches your task |
| `projects/` | Everything specific to one project | Working in any repo |
| `how-this-brain-works/` | The manual and design decisions for this brain | To set it up, or before proposing any change to it |

<!-- Always-loaded imports: Claude Code loads these files along with this one. Keep them
     within the budget in how-this-brain-works/README.md. -->
@principles/README.md
@when-to-use-skills/README.md
