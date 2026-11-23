---
summary: Lessons are significant mistakes, general by default, deduplicated by occurrence, and promoted or retired so the folder stays small.
read-when: Capturing a lesson, finding a similar one, or reviewing lessons for promotion.
---

# 0010 Lesson lifecycle

## Context
A human learns a lesson from a specific incident; if it keeps happening it hardens into a rule
of thumb or a habit, and the incidents fade. A list of every lesson would grow forever, and
every lesson first happens inside some project, which biases toward filing it there, where no
other project will see it.

## Decision
- Capture only "learned my lesson" mistakes, written from the owner's correction, each with a
  real example and a `read-when` cue for the start of a task.
- General by default: a lesson goes to the top level unless it can't be stated without one
  project's specifics.
- Search every lesson before writing; a match gets a new occurrence, and a match in another
  project gets proposed for the top level.
- Around three occurrences, or two projects, suggest promotion to a principle, a project
  tenet or domain concept, or a skill step; the owner decides. Promoted and retired lessons
  are deleted; git keeps them.

## Alternatives rejected
- **Capturing every correction:** buries the lessons that matter. Small mistakes may instead
  mean a skill needs fixing.
- **Project-level by default:** general lessons become invisible elsewhere, get written again,
  and never accumulate occurrences.
- **Keeping lessons forever:** the folder grows without bound.

## Consequences
Something must trigger promotion review: close-out suggests it when occurrences cross the
threshold, and an occasional consolidation pass catches the rest.
