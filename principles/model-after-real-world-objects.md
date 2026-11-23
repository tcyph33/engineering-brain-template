---
read-when: Deciding what a class, model, module, service, or API resource is, or where behavior belongs; or a framework requires an action-shaped class (controller, handler, worker, listener).
---

# Model after real-world objects

## In practice

Ask of every class, model, module, or resource: what real thing is this? If the answer is an
action ("it processes orders"), it isn't an object. It's a function on the thing it acts on.
Doer classes (`OrderProcessor`, `InvoiceManager`, `PriceCalculator`) are always wrong outside
framework plumbing.

| Instead of | Write |
|---|---|
| `OrderProcessor.process(order)` | `order.place()` |
| `EmailSender.send(email)` | `mailServer.deliver(email)` |
| `POST /processRefund` | `POST /orders/{id}/refunds` |

Put behavior on the thing that really has that responsibility. An email doesn't send itself;
in the real world a mail server delivers it, so that's where `deliver` lives.

## Framework plumbing

Some frameworks require classes shaped like actions: controllers, request handlers, job
workers, event listeners. Treat them as the framework's plumbing, not part of the model:

- Keep them thin: receive the input, call the domain objects, return the result.
- Put the real behavior on the domain objects they call.
- Don't create action-shaped classes the framework doesn't require.

## Tensions

- **No dumping grounds:** a real object can attract every behavior that touches it until it
  becomes a god class. Split it along the real things inside it (an order's line items, its
  shipping address), never into doer classes.
- **Reduce entropy:** existing code may already use doer classes. Don't add new ones; put the
  new behavior where it belongs if that's a contained change, and otherwise follow the
  existing structure and raise the restructuring as its own change.
