# Projects

Everything specific to one project. One folder per project, named the way people say it,
in kebab-case.

## Belongs here

Each project folder always has:

| File or folder | What it holds |
|---|---|
| `README.md` | What it's for, design tenets, how it's built, who relies on it, direction. Its frontmatter lists the project's repos. |
| `domain-concepts.md` | How this project models its domain, only where general knowledge would get it wrong. Present even when empty. |
| `dependencies/` | One note per thing this project relies on, and what it assumes about it. |
| `lessons-learned/` | Traps that only make sense with this project's specifics. |

## Doesn't belong here

- Knowledge that applies across projects → `principles/` or the top-level `lessons-learned/`.
- Decision records and design docs → the project's repos; notes here point at them.
- Anything the code already says plainly (file layout, signatures, setup steps).

## Finding a project

Search the `repos:` frontmatter in `projects/*/README.md` for the current repo's name.
See the project sections of `how-this-brain-works/README.md` for each file's format.
