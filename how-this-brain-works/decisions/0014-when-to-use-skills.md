---
summary: The brain records when the owner reaches for each skill, including the orchestrated flow, never what a skill does.
read-when: Adding a skill entry, or deciding whether a change should go through the orchestrated flow.
---

# 0014 When to use skills

## Context
A human knows their tools and when to reach for each, including when nobody asks. Skills are
useful outside the brain, so they live in the toolkit. Claude Code already shows each skill's
own description, which says what the skill does.

## Decision
`when-to-use-skills/` holds the owner's initiative and timing: situation first, then the exact,
fully qualified skill name. The orchestrated flow is itself a skill, and every change to a
project goes through it; its triage sizes how much process runs. The flow owns its stage
sequence; entries here cover using skills outside it.

## Alternatives rejected
- **Repeating skill descriptions:** two copies that drift.
- **Short skill names:** can resolve to a different skill with the same name.
- **Letting the agent decide a change is too small for the flow:** that unguided judgment is
  how small changes get over-engineered. The flow's light path must be nearly frictionless
  instead.

## Consequences
The orchestrated flow's name is not decided yet.
