# Changelog — review-filing

## [0.1.0] — 2026-05-15

### Added

- Initial alpha release.
- Resolves descriptors by name (against shipped `descriptors/`) or by
  explicit path; reads YAML frontmatter and structured body sections per
  the schema in `../shared/descriptor-schema.md`.
- Expands `include:` references against the `shared/checks/` library;
  resolves the single fan-out templating form
  `{{ each in case_params.<list> }}`.
- Prompts the attorney for any `case_params` the descriptor needs that
  weren't pre-supplied.
- Estimates evaluation cost up front and asks before proceeding; offers
  a `sample-first` mode for partial runs.
- Classifies documents to descriptor components; presents the
  classification table in the report so the attorney can spot
  misclassifications.
- Evaluates checks via vision (rendered-page evaluation) with Python
  bash helpers for text/metadata extraction.
- Produces a markdown report grouped by severity (block / warn / info)
  with page+region pointers, contextual reminders surfaced verbatim from
  the descriptor's prose section, and a staleness flag when the
  descriptor's `last_verified` is older than its `freshness_window`.
- Writes the report to `<filing_path>/.review-reports/` and also prints
  it to the session.

### Known issues / not-yet-implemented

- `evaluation_mode: acroform | hybrid | fingerprint` documented but fall
  back to `vision` at runtime.
- No firm-private descriptor override directory yet.
- No persistent cache between runs.
- Document classification on folders with non-standard filenames is
  likely to misclassify; the classification table is presented for
  attorney correction.
- `shared/claims/` library is empty in v0.1; `claim_elements_check`
  relies on the LLM's general knowledge of claim elements.
- Page-geometry predicates (`font_size_measurement`,
  `line_numbers_present`, `page_count_within`) are documented in the
  schema but unverified against real filings.
