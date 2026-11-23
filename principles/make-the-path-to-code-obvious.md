---
read-when: Creating, naming, or moving a file, folder, module, namespace, or package, or deciding where new code goes.
---

# Make the path to any code obvious from names alone ("bam, bam, bam")

## In practice

The test: take a question about behavior, such as "where do we decide an invoice is overdue?"
Could someone answer it by reading only folder and file names, without searching?

```
src/                              src/
  billing/                          controllers/
    invoice.ts    ← Invoice           InvoiceController.ts
    payment.ts                      services/
  shipping/                           InvoiceService.ts
    shipment.ts                     utils/
                                      dateHelpers.ts   ← isOverdue
```

On the left: billing, invoice, `isOverdue`. Bam, bam, bam. On the right, the folders name
technical layers, so you must know the architecture before you can find anything, and the
rule ends up in a helper named after neither the domain nor the thing it's about.

Organize by the domain, never by technical layer. Layers like `controllers/`, `services/`,
and `models/` are solution concepts, and a `services/` folder is usually where doer classes
collect. Every folder is a real namespace in the domain, even when it holds one file today:
it gives the code room to grow without reworking paths.

## Each file is named for what it holds

A file holds one main class or function, and its name is that thing's name, in the
language's file-naming convention: `Invoice` lives in `invoice.ts` (or `Invoice.java`).
Small private types that serve only that class or function may live in its file. Anything
else gets its own file.

If a file can't be named after one thing, it holds more than one: split it. Names like
`invoiceStuff.ts`, `billing.ts` holding six classes, or `types.ts` hide what's inside; see
the no-dumping-grounds principle.

## Tensions

- **Design first, then express it in the language:** some frameworks require plumbing in
  fixed places (`app/controllers/`, route folders). Put it where the framework requires and
  keep it thin; organize everything else by the domain.
