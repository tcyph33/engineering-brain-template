---
read-when: A framework requires a class shaped like an action (controller, request handler, job worker, listener).
---

# Model after real-world objects: framework plumbing

Classes always represent a real thing. Some frameworks require classes shaped like actions,
such as controllers, request handlers, job workers, and event listeners. Treat those as the
framework's plumbing, not part of the model:

- Keep them thin: receive the input, call the domain objects, return the result.
- Put the real behavior on the domain objects they call, never in the plumbing class.
- Don't create action-shaped classes the framework doesn't require.
