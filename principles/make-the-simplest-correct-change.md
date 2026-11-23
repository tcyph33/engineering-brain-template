---
read-when: Deciding how to make a change (what to add, where, and how much), or tempted to add an abstraction, option, or layer the ask didn't call for.
---

# Make the simplest change that is conceptually correct

## In practice

Start from the most direct change that does the ask. Then grow it only as far as conceptual
integrity requires, and stop there. Checking integrity includes what relies on the part
you're changing: its callers in the repo, consumers in other projects, and what each of them
assumes. Changing how a part works shouldn't affect them; changing what it promises always
does, however well it's designed.

Ask: "stop sending marketing emails to customers who unsubscribed."

1. **Most direct:** `if (!customer.unsubscribed)` before the send in the weekly newsletter job.
2. **Check integrity:** the rule is about all marketing email, not the newsletter.
   Promotions and abandoned-cart reminders are marketing too, so a check in one job makes
   the rule hold "except when…".
3. **Grow only that far:** put the rule where marketing recipients are chosen
   (`mailingList.recipients()` leaves out unsubscribed customers), so every marketing email
   follows it.
4. **Stop:** no preference center, no consent framework, no per-channel settings. The ask
   didn't call for them.

Stopping at step 1 hacks it; going past step 3 over-engineers it. Each thing added after the
most direct change must be needed to keep the concepts whole, and the result still follows
every other principle. So the simplest change is often bigger than the most direct one:
simplest isn't smallest.

When there's more than one way to keep the concepts whole, compare them the way
[design first](design-first.md) explores designs, and pick the simplest. If keeping the
concepts whole needs a concept the system doesn't have yet, stop and raise it as a design
decision. Don't add it quietly.

## Tensions

- **Isolate what's known to change:** isolating volatility can justify an abstraction the ask
  alone doesn't, but only with evidence that it will change, never "in case."
- **Treat difficulty as a design warning:** if no simple correct change can be found, the
  concepts may be wrong or missing. Raise it rather than settling for a hack.
