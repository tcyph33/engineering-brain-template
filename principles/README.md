# Principles

How to decide what to build and how. Always in mind. Not ranked: weigh them for the
situation at hand, and raise it when they conflict in a way that changes the design.

**Belongs here:** rules of judgment and design preferences that apply across projects. Each
one is a bold imperative plus a one-line why, linking to its `<name>.md` for how to apply it.
Only the owner of this brain adds or changes principles.

**Doesn't belong:** line- and routine-level coding rules (the coding-standards skill), one
project's design rules (its design tenets), specific mistakes (`lessons-learned/`).

## Principles

- **Build in terms of the domain, not the solution.** Name and shape everything (classes,
  objects, variables, APIs, data, docs) after the domain's real concepts, using general domain
  knowledge plus the project's `domain-concepts.md`. Never invent a domain concept; if a change
  needs one that isn't in either, raise it. *Why:* each piece of the system has a well-defined
  need and shape, which keeps the design conceptually coherent, and anyone who knows the domain
  can understand the solution. [How to apply it](build-in-terms-of-the-domain.md)
- **Model after real-world objects.** Classes, data models, modules, services, and API
  resources correspond to things that exist in the domain and carry the responsibilities those
  things really have. Actions are functions that act on objects; never turn an action into an
  object (no `OrderProcessor`, `InvoiceManager`). *Why:* real objects give stable,
  understandable boundaries, and behavior lives with the thing it belongs to, so a change lands
  in one place. [How to apply it](model-after-real-world-objects.md)
- **Strive to reduce entropy.** Every change keeps the system's original conceptual integrity:
  no special cases, no second way of doing something that already has a way, no concept that
  doesn't fit. Integrity erodes through many small changes, so each one has to hold the line.
  *Why:* entropy makes every change more expensive, until the codebase can't be edited safely
  or confidently and has to be thrown out and rebuilt. [How to apply it](reduce-entropy.md)
- **Make the simplest change that is conceptually correct.** Express the ask with the concepts
  the system already has: no new abstractions, interfaces, or layers, and no hacks that bend
  those concepts. Simplest isn't smallest; sometimes they're the same change, and sometimes a
  larger change in the right place is simpler than a small patch. If the ask can't be expressed
  with existing concepts, it needs a new concept: raise that design decision, don't make it
  quietly. *Why:* it completes the task and keeps conceptual integrity without over-engineering
  or hacking it, which a smallest-diff rule can't guarantee.
  [How to apply it](make-the-simplest-correct-change.md)
- **Make the path to any code obvious from names alone ("bam, bam, bam").** Directories and
  files, and namespaces and packages inside the code, are well-named namespaces named after the
  domain: someone who doesn't know the repo can drill from the root to the code they need just
  by reading names, without a wide search. Each file is named for the main class or function it
  holds. *Why:* people and agents find the right code quickly and with confidence, so they
  don't miss the piece that matters, and the structure itself explains the system.
  [How to apply it](make-the-path-to-code-obvious.md)
- **No dumping grounds.** No god classes, and no generic `utils`, `helpers`, `common`, `types`,
  or `misc` files. Each type and function gets its own file, placed closest to where it
  belongs; small private types that serve only one class or function may live in its file. Code
  shared across areas goes in their nearest common folder, named for what it is
  (`billing/money.ts`, not `shared/utils.ts`). Something with no natural home signals a missing
  or misplaced concept: find the concept rather than creating a catch-all. *Why:* catch-alls
  grow without limit, hide where things live, and blur the system's concepts.
  [How to apply it](no-dumping-grounds.md)
- **Keep the complexity anyone must hold in their head small.** Judge design choices by how
  much a person or agent needs to understand at once to work on one part safely, and prefer
  designs where each part can be understood on its own. *Why:* complexity, not code volume, is
  what makes software slow and risky to change; a system that can be understood one piece at a
  time stays workable as it grows, and someone missing context, person or agent, can still
  change one part without breaking another. [How to apply it](keep-complexity-small.md)
- **Isolate what's known to change.** When part of the system is known to be volatile (shifting
  business rules, an external system being replaced, a data format in flux), keep it behind one
  place so a change stays local. Only for volatility with evidence (the project's direction, a
  dependency being replaced, a rule that has changed before), never for imagined change. *Why:*
  a volatile detail spread across the code turns every change to it into a hunt; kept in one
  place, it's one edit. [How to apply it](isolate-what-changes.md)
- **Treat difficulty as a design warning.** When something is hard to name, hard to test, hard
  to explain without long comments, or keeps needing special cases, stop and fix the design
  rather than pushing through; if the fix needs a new concept, raise it. *Why:* the difficulty
  is a symptom of a concept that's wrong or missing, and working around it hides the problem
  and adds entropy. [How to apply it](treat-difficulty-as-a-warning.md)
- **Design first, then express it in the language.** Decide what the design should be (its
  concepts, boundaries, and responsibilities), exploring more than one design and choosing the
  simplest that is conceptually correct. Then build it with the language's and framework's
  tools; don't let what's easy or conventional in them shape the design. *Why:* a design bent
  to fit the tools drifts away from the domain; when the tools can't express the design
  directly, build the missing piece once rather than giving up the concept.
  [How to apply it](design-first.md)
