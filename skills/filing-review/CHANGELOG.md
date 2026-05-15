# Changelog — filing-review skill set

Tracks changes across both `review-filing`, `build-filing-descriptor`, and
their shared assets. Per-skill changelogs in `review-filing/CHANGELOG.md` and
`build-filing-descriptor/CHANGELOG.md` record skill-specific changes.

## [0.1.0] — 2026-05-15

### Added

- Initial alpha release.
- **`review-filing`** SKILL.md — reads a filing path and a descriptor name,
  resolves the descriptor, classifies documents to descriptor components,
  evaluates per-component and cross-document checks, and produces a markdown
  report grouped by severity (`block` / `warn` / `info`). Only
  `evaluation_mode: vision` is supported in alpha.
- **`build-filing-descriptor`** SKILL.md — interview flow that walks the
  attorney through identifying filing components, structure checks,
  cross-document checks (via `include:` from `shared/checks/`), free-form
  contextual rules, and assembly order; writes a descriptor file and
  optionally a new check or claim library entry.
- **`shared/descriptor-schema.md`** — canonical descriptor format spec.
  Documents YAML frontmatter, body sections, predicate vs free-form rules,
  the `include:` mechanism with the single fan-out templating form, severity
  levels, evaluation modes, and case_params.
- **`shared/checks/`** seed library:
  - `caption_consistency.yaml` — all pleadings in a filing must share the
    same caption (case number, party names).
  - `name_consistency.yaml` — a party's name across multiple documents
    matches under configurable normalization rules.
  - `signature_block_completeness.yaml` — signature + printed name + bar
    number + contact info + date present in each named document.
- **`descriptors/`** seed library:
  - `i-130-spouse-petition.md` — USCIS Form I-130 spouse petition.
  - `ca-pc-1538.5-motion-to-suppress.md` — California PC § 1538.5 motion
    to suppress evidence.
  - `cacd-civil-complaint.md` — federal civil complaint, US District Court,
    Central District of California (FRCP 8/9/10/11 + CACD local rules).

### Known limitations

- `evaluation_mode: acroform`, `hybrid`, and `fingerprint` are documented in
  the schema but not implemented in alpha. The skill should fall back to
  `vision` and surface a notice.
- The `shared/claims/` library is not shipped in this version. Descriptors
  that reference `claim_elements_check` (e.g., `cacd-civil-complaint.md`)
  will rely on the LLM's general knowledge of claim elements; expect drift.
- Page-geometry predicates (`font_size_measurement`, `line_numbers_present`,
  `page_count_within`) are documented in the schema but not exercised
  against real CACD filings — accuracy unverified.
- No firm-private descriptor override directory yet; descriptors must be
  passed by explicit path or resolved from this skill set's `descriptors/`.
- No persistent caching of evaluations between runs.
