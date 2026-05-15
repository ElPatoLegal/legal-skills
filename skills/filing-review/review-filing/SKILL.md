---
name: review-filing
description: "Review a legal filing (PDF or folder of PDFs) for completeness and compliance against a descriptor. Reads required components, per-component structure checks, and cross-document checks; classifies the filing's documents to the descriptor's components; evaluates each rule via vision; produces a markdown report grouped by severity. Trigger on: 'review the filing', 'check this filing', 'audit the I-130', 'review against descriptor', 'compliance check'."
practice_area: multi
jurisdiction: any (descriptor-specific)
author: Patrick Kolasinski
last_verified: 2026-05-15
freshness_window: 6 months
license: MIT
version: 0.1.0
---

> Licensed under the MIT License. See LICENSE in the repo root.
> Copyright in this skill is retained by its author(s) — see the YAML
> `author` field above and this file's Git history.
>
> [AI-ASSISTED DRAFT — requires attorney review. Not legal advice.
> No attorney-client relationship is created by use of this skill.]

# Review Filing

> **⚠️ ALPHA — actively developed, not verified to work well.** This skill
> is an early prototype. Reports may miss real defects, raise false
> positives, misclassify documents, or hallucinate. Do not file based on
> a report without independent attorney review of every line of the
> filing against the applicable rules. Treat the report as a draft
> worksheet, not a substitute for the attorney's own final-check pass.

## Purpose

Take a filing — either a single assembled PDF or a folder of separate
PDFs — and a descriptor name, run the descriptor's checks against the
filing, and produce a markdown report grouped by severity.

The descriptor defines what to check. This skill is the engine that
applies it.

## When to use

Attorney has assembled (or is reviewing) a filing and wants a structured
second-look against the descriptor's checklist before filing or as part
of a final review. Triggers include "review the filing," "check this
filing for completeness," "audit the I-130 package," "compliance check
against [descriptor]."

Not appropriate for: legal-strategy review, substantive-merit review of
arguments beyond what the descriptor's prose rules check, or any
adversarial drafting task. This is a checklist-style auditor, not a
brief reviewer.

## Inputs

- **`filing_path`** — required. Absolute or working-directory-relative
  path to a PDF or a folder of PDFs.
- **`descriptor`** — required. Either a descriptor name
  (`i-130-spouse-petition`) which resolves against the `descriptors/`
  folder, or an absolute path to a descriptor `.md` file.
- **`case_params`** — optional dict. The attorney may pre-supply values
  for any `case_params` the descriptor declares. Anything the descriptor
  needs that isn't supplied will be prompted.

## Operation

### 1. Resolve the descriptor

Look up the descriptor in this order:

1. If `descriptor` is a path that exists, use it directly.
2. Otherwise, look for `<descriptor>.md` in the working directory's
   `descriptors/` folder (firm-private override).
3. Otherwise, look for `<descriptor>.md` in this skill set's
   `descriptors/` folder (shipped community baseline).

If the descriptor's `schema:` field isn't recognized, stop and report —
do not guess.

### 2. Read the descriptor

Parse the YAML frontmatter strictly. Read the body's H2 sections —
`## Required components`, `## Per-component checks`, `## Cross-document
checks`, `## Conditional / contextual rules`, `## Assembly order`,
`## Filing destination`, `## Fee`.

For each `include:` reference, load the named file from
`shared/checks/<name>.yaml` (or `shared/claims/<name>.yaml` for claim
element checks) and resolve the `with:` parameters. Apply any
`override:` field substitutions.

Expand any fan-out `{{ each in case_params.<list> }}` templating.

### 3. Identify needed case_params

Compute the set of case_params the descriptor references (in
`required_when:` expressions and free-form rules). Compare to what the
attorney supplied plus what has defaults. For any unresolved param,
prompt the attorney before continuing.

### 4. Cost estimate and warning

Before running expensive vision passes, estimate cost:

- Identify total page count across the filing.
- Identify total number of per-component checks plus cross-document
  checks after include expansion.
- Rough heuristic: each vision-based check is one rendered page + one
  vision call; estimate ~$0.01–$0.05 per check depending on page
  complexity.

Surface an up-front estimate to the attorney:

```
The filing has ~N pages, and the descriptor declares ~M checks
requiring vision evaluation. Estimated cost: $X.XX–$Y.YY.
Proceed? (yes / no / sample-first)
```

If the attorney chooses `sample-first`, run on the first 1–2 documents
only and report partial results before continuing.

### 5. Classify documents to components

For each PDF in the filing, identify which component(s) of the
descriptor it represents:

- If the filing is a single assembled PDF, identify page ranges per
  component (cover page, I-130 form, exhibits, etc.).
- If the filing is a folder, classify each file by filename heuristics
  + first-page vision sampling.

Classifications are presented in the report so the attorney can correct
any misclassification before relying on the substantive findings.

A descriptor component with no document classified to it is reported as
**missing** with that component's severity (typically `block`).

A document classified to no component is reported as **unrecognized
extra material** (info-severity by default).

### 6. Evaluate checks

For each check (per-component and cross-document):

- **Atomic predicate** — apply the predicate per the schema's predicate
  reference. Use Python via Bash (pdfplumber, PyMuPDF) for text/metadata
  extraction; render-and-look-via-vision for visual checks; LLM
  reasoning for inherently judgmental checks.
- **Free-form `rule:`** — read the relevant page(s) (rendered or text)
  and evaluate the prose rule. Output: result + a one-sentence
  explanation.

Each check's evaluation_mode (per-check > per-component > descriptor
default) controls how it's evaluated. In alpha, treat any
non-`vision` mode as `vision` and note the fallback.

Apply `required_when:` predicates before evaluating; skip checks whose
condition isn't met.

For each evaluation, record:

- The check's label
- The component(s) it touches
- Pass / fail / skipped
- Severity (after override resolution)
- A one-line explanation
- Page+region pointer (if applicable) so the attorney can jump to it

### 7. Assemble the report

Output a markdown report with these sections, in order:

```markdown
# Review Report — <descriptor name>

**Filing:** <path>
**Descriptor:** <name> (schema <schema-version>; last_verified <date>)
**Case params:** <key-value pairs>
**Generated:** <ISO timestamp>

> ⚠️ AI-ASSISTED DRAFT — requires attorney review. Not legal advice.

## Summary

- BLOCKS: <count>
- WARNS: <count>
- INFOS: <count>
- Components: <X of Y identified>

## Document classification

| Document (file or page range) | Classified as | Confidence |
|---|---|---|
| ... | ... | ... |

**Unrecognized extra material:** <list>
**Missing components:** <list>

## BLOCK — must fix before filing

### <component or cross-check label>
- <one-line explanation>
- Source: <page, region>
- Rule: <descriptor section + line, or "include: <name>">

## WARN — likely RFE / objection / weakness

### ...

## INFO — observations

### ...

## Contextual reminders (from descriptor prose)

Surfaced verbatim from the descriptor's "Conditional / contextual rules"
section, with any prose practice notes the reviewer chose not to evaluate
mechanically.

## Filing destination and fee (from descriptor)

<surfaced verbatim from descriptor, with staleness flag if last_verified
is older than freshness_window>
```

### 8. Failure handling

- A single document that fails to open: log, skip its checks, surface in
  the report under a "Documents that could not be evaluated" section.
- A descriptor with a malformed `include:` (file not found, missing
  parameters): stop and report — do not silently skip.
- A descriptor referencing a predicate this skill doesn't implement:
  fall back to interpreting the predicate name as prose and evaluate via
  LLM reasoning; flag as `[alpha: predicate not natively implemented]`.

## Predicates (atomic checks)

See `../shared/descriptor-schema.md` for the predicate reference.

## Severity

- **`block`** — must fix before filing
- **`warn`** — likely defect; attorney attention needed
- **`info`** — observation

## Output location

The report is written as markdown to:

```
<filing_path>/.review-reports/<descriptor-name>-<ISO-date>.md
```

(or, for a single-PDF filing, alongside the PDF.) The report is also
printed to the chat session.

## Limitations (alpha)

- Only `evaluation_mode: vision` is fully supported. `acroform`,
  `hybrid`, and `fingerprint` modes fall back to `vision`.
- Document classification on folders relies on filename heuristics +
  first-page vision sampling. Misclassification on filings with non-
  standard filenames is likely; the classification table is presented
  for attorney correction.
- The `shared/claims/` library is not shipped in v0.1. Descriptors that
  use `claim_elements_check` fall back to the LLM's general knowledge
  of claim elements — accuracy varies by claim type.
- Court-day timeliness rules are deliberately out of scope.
- No persistent caching between runs. Re-running on the same filing
  re-evaluates every check.

## Output guardrail

Every report must include the prominent banner:

> ⚠️ AI-ASSISTED DRAFT — requires attorney review. Not legal advice.

Reports are starting points, not conclusions. The attorney is the final
reviewer.

## See also

- `../shared/descriptor-schema.md` — the canonical descriptor format
- `../build-filing-descriptor/SKILL.md` — authoring helper for descriptors
- `../descriptors/` — community-maintained descriptors
- `../CHANGELOG.md` — what changed across the filing-review skill set
- `./CHANGELOG.md` — what changed in this skill specifically
