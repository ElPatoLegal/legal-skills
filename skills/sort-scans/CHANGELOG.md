# Changelog — sort-scans

## [0.1.0] — 2026-05-14

### Added
- Initial release. OCR, identify, name, and file scanned legal documents into
  client folders on Windows via Claude Code CLI. Reads `conventions.md` and
  `staff-names.txt` from `references/`, processes PDFs in a `Scans/` root,
  files into `Sorted/` per firm conventions. Includes bundled scripts
  `ocr_files.py` and `extract_client_from_coversheet.py`.

### Changed (post-release)
- 2026-05-14 — added `author: Patrick Kolasinski` to YAML frontmatter and
  inserted generic in-file disclaimer block; no behavioral change.
