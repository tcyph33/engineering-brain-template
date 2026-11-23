# How This Brain Works

The operating manual for this brain. To start a brain or set one up on a machine, see
[Starting a new brain](#starting-a-new-brain) and [Setup](#setup). Read the rest before
adding, moving, or changing anything here. The reasons behind each rule are in
[`decisions/`](decisions/); when a rule seems inconvenient, read its decision before working
around it.

## The idea

This brain mimics how an experienced engineer's memory works. It is not documentation.

- **It holds what the code can't tell you:** what a product is for, the concepts and rules
  a design stays true to, what other systems we rely on and what we assume about them, and
  lessons learned the hard way. The test for any note: would a new senior hire need someone
  to tell them this?
- **It remembers the gist and knows where the details live.** Details stay in code and
  published docs. Before a note drives a decision, its pointers get checked, the way an
  engineer re-checks the details before acting on what they remember.
- **It grows from real work.** Gaps found while working get captured when the work is done,
  and lessons harden into principles over time.
- **Nothing outside knows it exists.** Code repos never reference the brain, and skills never
  reference it. The brain knows about repos and skills, never the other way around.

See [0001](decisions/0001-mimic-an-engineers-memory.md) and
[0002](decisions/0002-one-way-dependency.md).

## Starting a new brain

1. On GitHub, open
   [engineering-brain-template](https://github.com/tcyph33/engineering-brain-template) and
   choose **Use this template** to create a new **private** repo.
2. Follow [Setup](#setup).
3. Make it yours: the principles and skill entries are a starting point. The skills the
   entries name come from [claude-toolkit](https://github.com/tcyph33/claude-toolkit);
   install them or change the entries to skills you use.

See [0003](decisions/0003-self-contained-brains.md).

## Setup

The brain is loaded automatically in every Claude Code session. Below, `<brain>` is where you
cloned it, written from your home folder (for example `~/Github/software-engineering-brain`).
See [0005](decisions/0005-always-on-everywhere.md).

1. Clone the brain somewhere stable.
2. Create or edit `~/.claude/CLAUDE.md` and add one line importing the brain's root README:
   ```
   @<brain>/README.md
   ```
   Every session then gets the brain, and repos never mention it. The root README imports the
   other always-loaded files.
3. In `~/.claude/settings.json`, add an `ask` permission rule so any edit under the brain
   prompts first (merge it into existing `permissions` if there are any):
   ```json
   { "permissions": { "ask": ["Edit(<brain>/**)"] } }
   ```
   This only covers Claude's file-editing tools, not shell commands that write files. The
   real gate is that only you commit.
4. Check it: start a new session anywhere and ask what's in the brain's principles.

## How it's read

Three layers, like a person's working memory, recall, and looking things up:

| Layer | What's in it | When it's loaded |
|---|---|---|
| Always in mind | Root `README.md`, `principles/README.md`, `when-to-use-skills/README.md` | Every session, automatically |
| Recalled for the task | The project's `README.md` and `domain-concepts.md`; lesson summaries; dependency notes the change touches | Once it's clear what's being worked on |
| Looked up | A specific note's full text, then the code or docs its pointers lead to | Only when a decision depends on it |

**Always-loaded budget:** the three always-loaded files together stay under about 150 lines.
Every line costs context in every session and dilutes the principles. When the budget gets
tight, move detail into `<name>.md` files or split design preferences into their own
folder. Never merge principles to save space: each was made separate for a reason, and
which one applies more is decided by the situation.

**No indexes.** Folders don't list their notes. Find notes by scanning their frontmatter, for
example `grep -H -A1 "^summary:" lessons-learned/*.md`. The notes themselves are the only
source of truth for what's in a folder. The two always-loaded READMEs are the exception:
they hold the principles and skill entries themselves, not copies.

See [0005](decisions/0005-always-on-everywhere.md),
[0007](decisions/0007-three-reading-layers.md), and
[0008](decisions/0008-scan-notes-instead-of-indexes.md).

## Where knowledge goes

1. Is it about one project? → that project's folder. Otherwise, the top level.
2. Is it a mistake that cost real time, with a concrete example? → `lessons-learned/`
   (general by default; see Lessons).
3. Is it a rule of judgment or a design preference that applies across projects? →
   `principles/` (only the owner adds these).
4. Is it about when you reach for a skill? → `when-to-use-skills/`
5. Is it about something a project relies on? → that project's `dependencies/`
6. Is it what a project is for, its design rules, how it's built, or who relies on it? →
   that project's `README.md`
7. Is it how a project's model of its domain differs from the usual meaning? → that project's
   `domain-concepts.md`
8. Is it why a design choice was made? → a decision record in the repo it's about, not here
   ([0012](decisions/0012-decisions-live-in-repos.md)).
9. Is it a gap in a procedure (a skill should have caught it)? → fix the skill in the toolkit.
10. None of these fit? → don't force it. Flag it; the structure may need to grow.

## Note format

Every note is plain markdown with a small YAML frontmatter block. Folder READMEs and the root
README have no frontmatter.

```yaml
---
summary: One line. If someone reads only this, they still get the point.
read-when: The situation, at the start of a task, in which this note matters.
pointers:            # only if the note relies on something outside the brain
  - what: What the target is, so a broken pointer is still meaningful
    repo: org/repo-name
    path: path/to/file
    symbol: OptionalSymbolName      # optional; never line numbers
    verified: 2026-11-22 @ a1b2c3d  # date, plus commit for repo targets
  - what: A published doc
    url: https://...
    verified: 2026-11-22
status: active       # optional; stale or unverified quarantines the note
---
```

No `type`, `author`, `created`, or `updated` fields: the folder gives the type and git holds
the history.

**Exception:** a principle's or skill entry's `<name>.md` file has only `read-when`. Its
one-line summary lives in the always-loaded README, and repeating it would create a copy
that drifts.

**Body rules:**

1. One idea per note. If it needs headings for unrelated topics, split it.
2. Fits on about one screen. Longer usually means it restates code or holds two ideas.
3. Always state the why. A fact without its reason is something the code could have said.
4. Present tense, current truth. History and reasoning belong in decision records.
5. Don't restate code. Give the gist and point to the details.
6. Plain markdown only: standard relative links between notes, no wikilinks or plugin syntax.
7. Name files for their subject, in kebab-case.
8. Link text says what's behind the link: "see [why X is optional](...)", never "see [here](...)".
9. Mark anything unconfirmed as unconfirmed. That's what gets verified before relying on it,
   or asked about when there's nothing to check against.

See [0015](decisions/0015-plain-markdown.md).

## Pointers

The brain doesn't own what it points at, so pointers are weak references: checked before use,
never trusted blindly. See [0004](decisions/0004-weak-pointers-to-published-contracts.md).

- **Point at what's published.** Across project boundaries, point only at what the provider
  publishes (API specs, schemas, contracts, public docs), even when you own the provider.
  Within a project you work in, read the code directly rather than pointing at its internals.
  When a provider has no formal contract, point at whatever acts as one (the schema or type
  definition) and mark it `informal contract`.
- **Record identity, not just location.** `what` says what the target is, so a broken pointer
  still says what went missing.
- **Verify before relying.** When a note is about to drive a decision, follow its pointers
  and confirm they still say what the note claims.
- **When a pointer breaks:** search for the target by its identity (`git log --follow` within
  a repo; by name across repos and docs), propose the new location, and let the owner confirm.
  Never silently re-point. Mark the note `status: unverified` until it's resolved.
- **A move is information.** When something moves to a different repo or owner, ask whether
  the project's README (how it's built, who relies on it) needs updating too.

## Principles

`principles/README.md` holds each principle as a bold imperative plus a one-line why. They
are not ranked; which one weighs more depends on the situation. Every principle also has
`principles/<name>.md` for how to apply it: what it looks like in practice (good and bad
examples, real ones when you have them), how it pulls against other principles, and when it
doesn't apply. The file starts where the README line stops; repeating a big point is fine.

A good principle can be checked against a diff: someone could say whether a change follows
it. "Write clean code" fails that test. Only the owner of this brain adds or changes
principles; agents may propose them. See [0009](decisions/0009-unranked-principles.md).

## Lessons

```markdown
---
summary: Making a required field optional usually means relaxing the one check that enforces it, not new interfaces.
read-when: Asked to make a field optional, loosen validation, or accept data that's currently rejected.
occurrences:
  - 2026-10-14 in billing-api: asked to make customerId optional; agent added an input interface and adapter instead of relaxing the required check.
---

## What happened
## What to do instead
## Why
## Doesn't apply when    (optional)
```

- **Capture bar:** a "learned my lesson" mistake, one that cost real time or caused a real
  problem. Not every small correction.
- **Written from the owner's correction:** what they said the right change was and why, not
  the agent's own diagnosis of its mistake.
- **No real example, no lesson.** Without a concrete occurrence it's a guess at a principle.
- **`read-when` describes the situation at the start of a task,** when it can still be acted
  on, not the moment of the mistake.
- **General by default.** If it can be stated without naming anything specific to one
  project, it goes in the top-level `lessons-learned/`.
- **Search before writing.** Scan the summaries of every lesson, at both levels and in every
  project. If one matches, add an occurrence instead of a new file. If the match is in
  another project, propose moving it to the top level, reworded so it names neither project.

**Lifecycle:**

| Stage | What happens |
|---|---|
| Recurs | Add a line to `occurrences`. |
| About three occurrences, or two projects | Suggest promotion; the owner decides. It can become a principle, a project's design tenet or domain concept, or a step in a toolkit skill. |
| Promoted or retired | Delete the file. Git keeps the history. |

See [0010](decisions/0010-lesson-lifecycle.md).

## Projects

Each project folder always has `README.md`, `domain-concepts.md`, `dependencies/`, and
`lessons-learned/`. See [0011](decisions/0011-project-knowledge-shape.md).

### Project README

```markdown
---
summary: One line on what the project is.
repos:
  - org/repo-a
  - org/repo-b
---

# Project Name

## What it's for
Who uses it, what problem it solves for them, what it deliberately doesn't do. Name the
domain in plain words.

## Design tenets
At most about seven. Each one is a rule the whole design follows, with its why and what
would violate it, pointing at the repo's decision record when there is one.
- **Each repo owns its data.** Others read through its API or events, never its database.
  *Why:* repos can change internally without breaking each other. *Violated by:* one repo
  querying another's tables.

## How it's built
A few sentences: each repo's role, what it owns, and the main flow through them.

## Who relies on this
Known consumers outside this brain, what they use, and what they assume, marked confirmed
or unconfirmed. Consumers that are projects in this brain are found from their dependency
notes and aren't listed here.

## Direction (as of YYYY-MM)
Where it's heading, what's being replaced, what not to build new things on.

## Go deeper
domain-concepts.md, dependencies/, lessons-learned/, and pointers to design docs and decision
records in the repos.
```

The brain holds what you need to *judge whether a change fits*. Design docs and decision
records, in the repos, hold what you need to *build it*. If a project needs more than about
seven tenets, some are implementation details that belong in a design doc. Cross-project rules
go in the shared provider's tenets, since every project that depends on it reads its README.

### Domain concepts

`domain-concepts.md` holds how this project models its domain, only where general domain
knowledge would get it wrong. It exists in every project. If there's nothing to say, it says
so on purpose: *No project-specific domain concepts. General domain knowledge applies as-is.*

```markdown
---
summary: How <project> models <domain>, and where it departs from the usual meaning.
read-when: Naming or modeling anything in <project>, or when a term's meaning matters.
---

# <Project> domain concepts
Only what general knowledge would get wrong.

## The model in brief
How the core concepts relate, in a few sentences.

## Invoice
A request for payment for one completed order.
- **Differs from the usual meaning:** never edited after it's issued; corrections are credit
  notes. Why: audit requires an unaltered record.
- **Rules:** voided only before any payment.
- **Don't call it:** bill, statement.
- **In code:** only if the code's name differs from the domain term.
```

Lifecycles and relationships go in only when the code can't show them, for example when they
span several repos. An entry with nothing that differs, no rules, and no naming trap is a
definition general knowledge already has: cut it. Over about two screens means the project
spans several domains or the file is drifting into a dictionary.

### Dependencies

One note per thing the project relies on, named for it: other teams' systems and your own
projects alike. See [0013](decisions/0013-interactions-are-dependencies.md).

```markdown
---
summary: What we use it for and the key thing we rely on.
read-when: Changing how this project uses <thing>, or when <thing>'s behavior matters.
depends-on: <thing's name, or the project's folder name if it's in this brain>
pointers:
  - what: <the published contract>
    ...
---

# <Thing>
**Owned by:** <team name; or "this brain" with a link to the project's README>

## What we use it for
## What we rely on
Each assumption, marked *Confirmed: <source>* or *Unconfirmed*.
## Quirks
Facts about it that surprise people.
```

- `depends-on` is how consumers are found: grouping every dependency note by `depends-on`
  gives each provider's consumers within this brain. The root README has agents search it
  before changing anything another project could use.
- Don't describe the provider's API or internals, where our code calls it, or anything the
  provider's own README in this brain already says.

### Project lessons

Same format and lifecycle as top-level lessons, for lessons that only make sense with this
project's specifics.

## Skill usage

`when-to-use-skills/README.md` holds one line per situation: the situation first, then the
exact, fully qualified skill name (for example `code-review:code-review`, not `code-review`,
which can resolve to a different skill). It records when the owner reaches for a skill,
including when nobody asks, never what the skill does.

Every change to a project goes through the orchestrated flow skill, which sizes the process
itself; don't decide up front that a change is too small for it. The flow owns its stage
sequence; entries here cover using skills outside it. See
[0014](decisions/0014-when-to-use-skills.md).

## Changing the brain

- **Read-only during normal work.** Agents propose changes; the owner approves them.
- **Every write asks first.** A permission rule (see Setup) prompts before any file under the
  brain is created or edited.
- **Only the owner commits.** Agents never commit to the brain. The owner reviews the diff and
  commits, which also catches anything written outside the normal file tools.
- **Framework changes go to the template too.** If you maintain the template this brain came
  from, make any change outside `projects/` and the notes in `lessons-learned/` in both repos.
  See [0003](decisions/0003-self-contained-brains.md).

See [0006](decisions/0006-gated-writes.md).

## Not built yet

- **Lint:** a script in this folder that checks frontmatter, verifies pointers still resolve,
  flags notes whose sources changed since `verified`, flags files in unknown places, checks
  the always-loaded budget, and lists consumers by `depends-on`. Until it exists, these checks
  are manual. See [0016](decisions/0016-brain-maintains-itself.md).
