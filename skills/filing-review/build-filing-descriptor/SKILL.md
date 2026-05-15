---
name: build-filing-descriptor
description: "Interview-style authoring helper for descriptors used by `review-filing`. Walks the attorney through identifying filing components, structure checks, cross-document checks, free-form contextual rules, and assembly order; writes a descriptor file and optionally a new check or claim library entry. Trigger on: 'build a descriptor', 'create a descriptor', 'help me write a descriptor', 'add a new filing type', 'modify the descriptor'."
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

# Build Filing Descriptor

> **⚠️ ALPHA — actively developed, not verified to work well.** This skill
> is an early prototype. Descriptors it produces may have schema-conformance
> bugs, miss important checks, or capture rules incorrectly. Review every
> descriptor before relying on it; run the `review-filing` skill on a
> known-good and a known-defective sample filing before treating a
> descriptor as production-ready.

## Purpose

Conversationally walk an attorney through producing a descriptor that
the `review-filing` skill can evaluate against. The output is a single
`.md` file conforming to the schema in
`../shared/descriptor-schema.md`. Optionally also adds reusable named
checks to the `shared/checks/` library or claim entries to
`shared/claims/`.

## When to use

Attorney wants to add support for a filing type the existing descriptors
don't cover, or wants to modify an existing descriptor (different
jurisdiction, different firm conventions, different default severities).
Triggers: "build a descriptor for X," "help me write a descriptor,"
"add a new filing type," "modify the I-130 descriptor for [variant]."

Not appropriate for: writing actual SKILL.md files (this skill produces
descriptors only), drafting legal documents, or evaluating an existing
filing (that's `review-filing`).

## Inputs

- **`filing_name`** — what is the filing? Free text; this becomes the
  basis for the descriptor's `name` and filename.
- **`jurisdiction`** — what governs?
- **`existing_descriptor`** — optional. If modifying an existing
  descriptor, the path or name.
- **`sample_filing_path`** — optional. If provided, this skill can run
  the descriptor against the sample at the end to surface obvious gaps.

## Operation

### 1. Identification (5 min)

Ask the attorney:

- What filing type? (e.g., "California PC § 1473.7 motion to vacate")
- What jurisdiction governs? (federal? state? which court?)
- Is there a standardized form, or is this caption-paper pleadings, or
  a mix?
- Roughly how many separate documents are in a complete filing?
- Is the filing typically e-filed or paper-filed, and where?

Capture answers; these become frontmatter (`name`, `description`,
`jurisdiction`, `forms_supported`).

### 2. Case parameters (5–10 min)

Ask: what variables change how this filing should look?
Examples by filing type:

- Immigration form filing: petitioner status, relationship,
  prior marriages, beneficiary location.
- Criminal motion: hearing stage, search type, county.
- Civil complaint: jurisdictional basis, claim types, presence of
  corporate parties, related cases.

For each variable, ask:
- What values are possible? (enum, int, free text, bool)
- Is there a sensible default?
- When is it required? (always, or only under some condition)

Capture as `case_params` in frontmatter. `filing_date` is implicit (no
need to ask).

### 3. Required components (10–20 min)

Ask: what documents/forms/exhibits must be in a complete filing?

For each component:
- Component type: `form`, `pleading`, or `exhibit`
- Identifier (kebab-case)
- Severity if missing (`block` by default for must-have items)
- Conditional? (`required_when:` prose, referencing case_params)
- Acceptable variants if any (`accepts:` list)

Capture as the `## Required components` section.

### 4. Per-component structure checks (15–30 min per component)

For each component, walk through what makes that component complete and
defect-free:

- **For forms**: which fields/sections must be filled? Which signatures?
  Which dates? Pull the structure from the actual form if possible (ask
  the attorney to share a sample). Each field becomes a check entry
  with `label:`, `predicate:` (or `rule:`), `severity:`.
- **For pleadings**: what does the document's structure look like?
  Caption requirements, required sections (statement of facts, legal
  argument, conclusion, signature block, penalty-of-perjury clause).
  Each becomes a check.
- **For exhibits**: usually fewer structural checks (existence + some
  metadata). The interesting work for exhibits is cross-document
  consistency in the next step.

Suggest format-as-measurement checks for filings with strict formatting
rules (CACD: 14-point proportional font, line numbers; California
Judicial Council: specific caption block; etc.). Surface from the
attorney whether these matter.

Capture as `## Per-component checks`.

### 5. Cross-document checks (15–20 min)

Ask: what should be consistent between two or more documents in this
filing?

Walk through the named-check library (`../shared/checks/`) and offer
each by name:

- `caption_consistency` — pleadings carrying the same caption?
- `name_consistency` — a party's name matching across documents?
- `signature_block_completeness` — signature blocks complete?
- `identifier_consistency` — A-numbers, case numbers, receipt numbers?
- `period_coverage` — address/employment/residence history covers a
  target window?
- (Library will grow with each new descriptor.)

For each that applies, ask the attorney to fill in the `with:`
parameters. If a needed cross-check isn't in the library, draft a
one-off entry inline AND ask whether to promote it to a new library
entry (see step 7).

Pay particular attention to **exhibit-vs-pleading consistency** — the
factual claims in pleadings should not contradict the exhibits they
purport to summarize. Use the `factual_consistency` named check or a
free-form `rule:`.

Capture as `## Cross-document checks`.

### 6. Free-form contextual rules (5–10 min)

Ask: what else should the reviewer check that doesn't fit a structured
check? What practice notes should be surfaced verbatim with every
report?

Examples:
- "Divorce decree dates must precede current marriage date."
- "For Franks challenges, the declaration must plead specific false
  statements with offer of proof."
- "Defendants named in caption but never referenced in any count is a
  red flag."

Capture as bullets in `## Conditional / contextual rules (free-form,
LLM-evaluated)`.

### 7. Promote one-offs to the library (optional, 5 min)

If a one-off cross-document check or per-component check looks
generally reusable, offer to promote it:

- New entry in `../shared/checks/<name>.yaml`.
- Parameters factored out so the entry is reusable across descriptors.
- Default severity set.

The promoted check gets a corresponding entry in the parent
`CHANGELOG.md`.

### 8. Assembly order (5 min)

Ask the attorney for the expected order documents appear in a complete
package. Capture as `## Assembly order`.

### 9. Filing destination and fee (3 min)

Ask: where does this get filed? Court address? CM/ECF docket? E-filing
service? What's the current fee?

Capture as `## Filing destination` and `## Fee`. Flag explicitly that
fees should be re-verified before filing (`[VERIFY]`).

### 10. Validate against a sample (optional, 10–20 min)

If the attorney provided a `sample_filing_path`, invoke the
`review-filing` skill on the sample using the new descriptor. Walk
through the resulting report with the attorney:

- False positives: tighten the relevant check or downgrade its severity.
- False negatives (defect the attorney can see but the report missed):
  add a new check or strengthen an existing one.
- Misclassifications: refine component identifiers or filename
  heuristics.

Iterate until the descriptor produces results the attorney trusts.

### 11. Write the descriptor

Output paths (the skill chooses based on context):

- **Adding a new community descriptor**: write to
  `../descriptors/<name>.md` and add a CHANGELOG entry. Ask whether to
  open a PR.
- **Firm-private descriptor**: write to a path the attorney specifies
  (typically a firm-private repository or local directory). The attorney
  is responsible for syncing.
- **Modifying an existing descriptor**: overwrite the source file with
  the revised content. Show a diff to the attorney before writing.

Every descriptor produced by this skill must include:
- YAML frontmatter (required fields per the schema)
- The standard in-file disclaimer block (per repo template)
- An H1 title
- The body sections in the conventional order

## Output structure

Produced descriptor files follow this skeleton:

```markdown
---
name: <kebab-case-name>
description: "..."
jurisdiction: ...
schema: 0.1
evaluation_mode: vision
default_severity: warn
forms_supported: [...]
case_params: [...]
last_verified: YYYY-MM-DD
freshness_window: 6 months
author: <Attorney Name>
license: MIT
---

> Licensed under the MIT License. See LICENSE in the repo root.
> Copyright in this descriptor is retained by its author(s) — see the
> YAML `author` field above and this file's Git history.
>
> [AI-ASSISTED DRAFT — requires attorney review. Not legal advice.
> No attorney-client relationship is created by use of this descriptor.]

# <Filing Type Title>

## Required components
...

## Per-component checks
...

## Cross-document checks
...

## Conditional / contextual rules (free-form, LLM-evaluated)
...

## Assembly order
...

## Filing destination
...

## Fee
...
```

## Output guardrail

Every descriptor produced by this skill carries the prominent disclaimer
block. The skill never writes a descriptor without it.

The skill also surfaces in chat that the new descriptor is alpha and
should be validated against at least one known-good filing before being
trusted on a real matter.

## Limitations (alpha)

- The interview is unguided by validation — if the attorney describes
  checks that don't match a known predicate and aren't expressible as
  reasonable free-form rules, the skill will produce a descriptor that
  the reviewer may not handle well. Test against a sample filing before
  trusting.
- No structural validation of the produced descriptor against the schema.
- No version control of descriptors beyond what the attorney commits
  manually.
- The community-vs-firm-private path decision is heuristic in alpha;
  expect to specify the output path explicitly.

## See also

- `../shared/descriptor-schema.md` — the schema this skill produces
- `../shared/checks/` — the named-check library
- `../review-filing/SKILL.md` — the skill that consumes descriptors
- `../CHANGELOG.md` — what changed across the filing-review skill set
- `./CHANGELOG.md` — what changed in this skill specifically
