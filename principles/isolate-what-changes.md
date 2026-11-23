---
read-when: Part of the system is known to change (the project's direction says so, a dependency is being replaced, a rule has changed before), or tempted to add an abstraction in case something changes.
---

# Isolate what's known to change

## In practice

The test: can you point to evidence that this part will change? Each row below shows a
kind of evidence. "We might switch databases someday" and "it'd be more flexible" are not
evidence.

| Evidence it will change | Isolated |
|---|---|
| git history: tax rates changed in each of the last three years | rates kept in one place, read through `taxRate(region, date)` |
| a dependency is being replaced: the payment provider | one `paymentProvider` module; nothing else imports the vendor's SDK |
| the project's direction: notifications move from email to push | one `notify(customer, message)`; nothing else knows the channel |
| the user says shipping rules change with each carrier contract | the rules live in `shippingPolicy`, not as conditions across checkout |

Isolated means a change to the volatile thing is one edit, and nothing outside that place
knows its details.

Common misuse: an interface with one implementation "so we can swap it later," or a setting
for a value that has never changed. Both add a concept the system doesn't need yet.

When evidence that a part will change shows up later (a new tax region is announced, a
vendor is being dropped), isolate that part then, as its own change before the change that
needed it: first make the change easy, then make the easy change.

## Tensions

- **Make the simplest change:** isolation adds more than the ask needs; evidence is the only
  thing that justifies it.
- **Keep complexity small:** the isolating layer is one more thing to understand, but it
  saves knowing the volatile details everywhere. That trade only pays with evidence.
