# Changelog

Repo-wide history of skill additions and changes. Per-skill changelogs live in
each skill folder (`skills/<skill>/CHANGELOG.md`).

Format loosely follows [Keep a Changelog](https://keepachangelog.com/). Dates
are ISO-8601. Skill version bumps follow the version field in each SKILL.md.

---

## [Unreleased]

### Added
- `filing-review/` skill set (alpha, v0.1.0)
  - `review-filing` — reviews a filing (PDF or folder) against a descriptor
    that declares required components, per-component structure checks, and
    cross-document checks. Supports vision-based evaluation only in alpha.
  - `build-filing-descriptor` — interview-style authoring helper for
    descriptors and named-check library entries.
  - Three example descriptors: I-130 spouse petition, California PC § 1538.5
    motion to suppress, and CACD civil complaint.
  - Three named library checks: caption consistency, name consistency,
    signature block completeness.
- Repo-wide `CHANGELOG.md` (this file).
- Per-skill `CHANGELOG.md` files for `sort-scans` and the `filing-review` set.

### Changed
- README — added prominent alpha-status banner and updated skills table.

---

## 2026-05-14

### Changed
- LICENSE — copyright holder now reads "Patrick Kolasinski and contributors"
  rather than the brand, matching the standard open-source pattern.
- CONTRIBUTING.md — added a "License of Contributions" section spelling out
  inbound = outbound MIT and that contributors retain copyright in their
  individual skills; added `author:` field to the SKILL.md template; included
  a generic in-file disclaimer block in the template.
- README.md — replaced the one-line "License" note with a full "License &
  Disclaimer" section.
- `.claude-plugin/plugin.json` — author field normalized to
  `"Patrick Kolasinski (ElPato Legal)"`.
- `skills/sort-scans/SKILL.md` — added `author: Patrick Kolasinski` to YAML
  frontmatter and inserted the generic in-file disclaimer block between
  frontmatter and the H1.

---

## 2026-05-14 — initial repo scaffold

### Added
- `sort-scans` skill (v0.1.0) — OCR, identify, name, and file scanned legal
  documents into client folders.
- Initial scaffold: `plugin.json`, `README.md`, `CONTRIBUTING.md`, MIT
  `LICENSE`, `skills/` directory.
