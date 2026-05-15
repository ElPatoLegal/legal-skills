# Changelog — build-filing-descriptor

## [0.1.0] — 2026-05-15

### Added

- Initial alpha release.
- 11-step interview flow: identification → case parameters → required
  components → per-component checks → cross-document checks (drawn from
  the named-check library where possible) → free-form contextual rules
  → optional library promotion → assembly order → filing destination
  and fee → optional validation against a sample filing → write to disk.
- Writes descriptors conforming to schema v0.1 in
  `../shared/descriptor-schema.md`, including the standard YAML
  frontmatter, in-file disclaimer block, and conventional body sections.
- Offers to promote one-off cross-document or per-component checks to
  reusable entries in `../shared/checks/`.
- Optionally runs `review-filing` on a sample filing at the end to
  surface false positives and false negatives before the descriptor is
  treated as production-ready.

### Known issues / not-yet-implemented

- No structural validation of the produced descriptor against the
  schema. A malformed descriptor will only surface when `review-filing`
  fails to parse it.
- No version control of descriptors beyond what the attorney commits
  manually.
- The community-vs-firm-private output path is heuristic — expect to
  specify the path explicitly.
- The skill cannot directly create PRs to the community repo; it can
  produce the descriptor file and a CHANGELOG entry, and the attorney
  opens the PR through their own tooling.
