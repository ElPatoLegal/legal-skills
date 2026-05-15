# Descriptor schema (v0.1, alpha)

A descriptor describes one type of filing — what documents it must contain,
what each document must look like, and how the documents must be consistent
with each other. The `review-filing` skill reads a descriptor and applies
its checks to an actual filing. The `build-filing-descriptor` skill is an
interview-style authoring helper that produces descriptors in this format.

**Status.** This schema is a draft. Breaking changes are expected. The
schema version is declared at the top of each descriptor (`schema: 0.1`).
Future versions may rename fields or restructure sections; tools should
fail loudly when they see a `schema:` they don't recognize.

## File format

A descriptor is a single `.md` file with two parts:

1. **YAML frontmatter** between `---` delimiters at the top of the file —
   strict YAML, machine-readable.
2. **Markdown body** with conventional H2 sections (`## Required
   components`, `## Per-component checks`, etc.). YAML blocks inside the
   body — wrapped in triple-backtick `yaml` fences — carry the
   machine-readable check definitions. Prose between blocks is contextual
   guidance the reviewer reads as additional evaluation context.

The boundary is deliberately fuzzy: structured YAML for the parts the
reviewer needs to mechanically enumerate (component list, per-check
locator + predicate + severity), free-form prose for everything else.

## Frontmatter

```yaml
---
name: <kebab-case-id>                  # required; matches filename stem
description: "<one-line summary>"      # required
jurisdiction: <text>                   # required; e.g. "federal (USCIS)"
schema: 0.1                            # required; this schema version
evaluation_mode: vision                # default for all components; see below
default_severity: warn                 # default when a check omits severity
forms_supported:                       # optional; standardized forms this
  - {id: <form-id>, editions: [...], cite: "<optional citation>"}
case_params:                           # parameters the descriptor needs to
  - {key: <name>, type: <type>, ...}   # know to evaluate; reviewer prompts
                                       # the attorney for any not provided
last_verified: YYYY-MM-DD              # per repo convention
freshness_window: <duration>           # per repo convention
author: <Name>                         # per repo convention
license: MIT
---
```

`case_params` types: `string`, `int`, `number`, `bool`, `date`, `time`,
`enum` (with `values:` list), `list[enum]`, `list[doc-id]`. Each may
specify `default:`, `optional: true`, `required_when: "<prose>"`, and free-
form `notes:`.

Every descriptor implicitly receives `filing_date` (type `date`, default
`today`) — used as the anchor for date arithmetic.

## Body sections

### `## Required components`

A YAML list of every document the filing must contain. Three component
types are recognized:

| Type | Meaning |
|---|---|
| `form` | Standardized fillable form (USCIS, Judicial Council, AO forms). Has field-level structure. |
| `pleading` | Caption-paper document drafted from scratch (notice of motion, memo, declaration, complaint). |
| `exhibit` | Attached supporting material (police reports, marriage certificates, search warrants, etc.). |

Each entry carries an `id`, a `severity`, and optional `required_when`,
`accepts` (list of acceptable concrete document types), and `notes`.

```yaml
- form:     {id: i-130, severity: block}
- pleading: {id: declaration_of_counsel, severity: block,
             required_when: "search_type == warrantless"}
- exhibit:  {id: marriage_certificate, severity: block,
             notes: "Certified copy + English translation if non-English."}
```

### `## Per-component checks`

Subsections per component (`### <component-id>`) listing structure checks.

Each check is either:

- **Atomic** — uses a known predicate the runtime can evaluate:

  ```yaml
  - {label: "Part 1, Item 1 — Petitioner family name",
     predicate: field_present,
     severity: block}
  ```

- **Free-form** — prose the LLM evaluates:

  ```yaml
  - {label: "Statement of facts section is non-conclusory",
     rule: "the statement of facts states facts without legal conclusions or characterizations of the search",
     severity: warn}
  ```

A check uses **either** `predicate:` **or** `rule:`, never both.

A check may also override the component's evaluation mode:

```yaml
- {label: "Proportional 14-point font (CACD L.R. 11-3.1.1)",
   predicate: font_size_measurement,
   params: {min_pt: 14, scope: body},
   evaluation_mode: vision,
   severity: block}
```

### `## Cross-document checks`

A YAML list of checks that span two or more components. Use the `include:`
mechanism to pull from the shared library:

```yaml
- include: caption_consistency
  with:
    docs: [notice_of_motion, memorandum, declaration_of_counsel, proof_of_service]
  override:
    severity: block
```

Or write a one-off cross-document check inline:

```yaml
- beneficiary_dob_consistency:
    sources:
      - {doc: i-130, locator: "Part 2 Item 11 DOB"}
      - {doc: i-130a, locator: "Part 1 DOB"}
    predicate: dates_exact
    severity: block
```

### `## Conditional / contextual rules (free-form, LLM-evaluated)`

A markdown bullet list of prose rules. The reviewer reads each as an
instruction to evaluate against the whole filing. Severity defaults to
`default_severity`; bullets may override with `[severity: block]` at the
end.

### `## Assembly order`

Numbered markdown list. The reviewer checks whether the filing matches
the order. Order mismatch defaults to `warn` unless overridden.

### Other conventional sections

- `## Filing destination` — informational; reviewer surfaces verbatim.
- `## Fee` — informational; reviewer surfaces verbatim, flags any
  staleness based on `last_verified`.
- `## Notes` — informational.

## Predicates (atomic checks)

The runtime recognizes the following predicate names. Predicates whose
name ends in `_measurement` operate on rendered pages (vision +
PDF-metadata extraction). All others operate on extracted text or vision.

| Predicate | Meaning |
|---|---|
| `field_present` | A named form field is filled in. |
| `signature_present` | A signature glyph or AcroForm signature appears at a named location. |
| `date_present` | A date is filled in at a named location. |
| `names_match` | Two or more name strings refer to the same person under specified normalization. |
| `dates_exact` | Two or more dates are identical. |
| `places_match` | Two or more place references resolve to the same jurisdiction. |
| `identifiers_exact` | Two or more identifier strings (A-numbers, case numbers, receipt numbers) match exactly after stripping formatting. |
| `case_number_and_party_names_exact` | Caption blocks are identical across documents. |
| `period_coverage` | A set of date ranges covers a target window with at most `allow_gaps_up_to_days` of gap. |
| `duration_sum` | Sum of durations across a set of ranges meets a threshold. |
| `date_before` | One date precedes another. |
| `date_after` | One date follows another. |
| `age_at_event` | Age computed from a DOB and a reference date meets a comparison. |
| `font_size_measurement` | Body font size meets a minimum point threshold. |
| `line_numbers_present` | Left-margin line numbers are present. |
| `page_count_within` | Page count meets a maximum. |
| `party_lists_match_exactly` | Party lists across documents are character-identical. |
| `amounts_match_or_complaint_states_exceeds_threshold` | Amounts in controversy reconcile across documents. |

When in doubt, use free-form `rule:` prose — the LLM is usually competent
enough to evaluate something the schema doesn't have a predicate for.

## The `include:` mechanism

Reusable named checks live in `shared/checks/<name>.yaml`. A descriptor
pulls one in by name:

```yaml
- include: <check-name>
  with:
    <param>: <value>
  override:
    severity: <new-severity>
```

`with:` supplies the parameters the check declares. `override:` (optional)
replaces fields on the resolved check — typically just `severity:`.

### Fan-out templating (the one form that exists)

If a parameter is a list, an `include:` block may fan out via a small
templating form:

```yaml
- include: claim_elements_check
  with:
    claim_type: "{{ each in case_params.claim_types }}"
    locator: "the count alleging this claim in the complaint"
    severity: block
```

This expands to one invocation per entry in `case_params.claim_types`.
**This is the only templating the schema supports.** No general
expressions, no loops, no branching. The reviewer evaluates the include
once per item and folds the results into the report.

### Library check file format

```yaml
# shared/checks/<name>.yaml
name: <name>
description: <one-line>
parameters:
  - {key: <name>, type: <type>, required: <bool>, notes: "..."}
predicate: <predicate-name>     # OR
rule: "<free-form prose>"
default_severity: <severity>
notes: |
  Optional multi-line notes — surfaced by the reviewer when the check
  fires.
```

A library entry uses either `predicate:` or `rule:` (same rule as inline
checks).

## Severity

Three levels:

- **`block`** — defect would cause the filing to be rejected, returned, or
  fatally defective. The report leads with these.
- **`warn`** — defect is likely to cause an RFE, motion to strike,
  remediable rejection, or substantive weakness. Surfaced prominently.
- **`info`** — observation worth surfacing but not necessarily a defect.

Severity is declared per check. The descriptor's `default_severity:`
applies when a check omits one. `block` is never the implicit default —
require it explicitly.

## Evaluation modes

Declared at the descriptor (`evaluation_mode:` in frontmatter, default
for all components) or overridden per component or per check.

- **`vision`** — rendered-page vision evaluation. The only fully-supported
  mode in alpha.
- **`acroform`** — extract from the PDF's AcroForm field layer. Documented
  but not implemented in alpha.
- **`hybrid`** — try AcroForm first, fall back to vision. Documented but
  not implemented in alpha.
- **`fingerprint`** — use a confirmed AcroForm-name-to-human-label map for
  a specific form edition. Documented but not implemented in alpha.

When a non-`vision` mode appears in a descriptor and the runtime can't
honor it, the runtime falls back to `vision` and surfaces a notice.

## Out of scope (deliberately)

- **Court-day arithmetic.** Anything depending on a judicial calendar
  (weekends, judicial holidays, department closures) is out of scope.
  Procedural timeliness rules belong in the prose body as practice
  reminders the reviewer surfaces verbatim.
- **Cost optimization.** The reviewer estimates cost up front and warns
  the attorney. Aggressive optimization (e.g., text-extraction-first
  triage to skip vision when text suffices) is planned, not alpha.
- **Firm-private descriptor override directories.** For now, descriptors
  resolve from the shipped `descriptors/` folder or an explicit path.
