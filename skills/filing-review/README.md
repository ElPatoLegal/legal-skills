# filing-review — review a filing against a configurable descriptor

> ## ⚠️ ALPHA — ACTIVELY DEVELOPED — NOT VERIFIED TO WORK
>
> **This skill set is an alpha. It has not been independently confirmed
> to produce correct results on any real filing.** Outputs may miss
> defects, raise false positives, misclassify documents, or hallucinate.
> Descriptor schemas, the named-check library, and skill interfaces will
> change without notice between versions.
>
> **Do not file anything based on a report produced by this skill without
> independent attorney review of every line of the filing against the
> applicable rules.** Treat the report as a draft worksheet that flags
> things worth a second look — not as a substitute for the attorney's own
> final-check pass.
>
> Particular things that may not work yet: classification of documents
> into descriptor components; vision-based form-field checks on heavily
> annotated or low-quality scans; substantive consistency checks across
> exhibits; element-by-element claim review for unfamiliar causes of
> action.

This folder contains two related skills plus their shared assets:

- **`review-filing/`** — takes a filing (PDF or folder of PDFs) and a
  descriptor name, runs the descriptor's checks against the filing, and
  produces a markdown report grouped by severity.
- **`build-filing-descriptor/`** — interview-style authoring helper for
  descriptors and for adding new entries to the named-check library.
- **`shared/`** — descriptor schema spec, named-check library
  (`shared/checks/`), and (later) claim-element library (`shared/claims/`).
  Both skills read from this folder.
- **`descriptors/`** — community-maintained descriptors. Both skills look
  here for descriptors by name.

The two skills are co-developed and share a vocabulary; the parent folder
ships them together so you don't end up with one without the other.

## Quick start

In a Claude Code session with this plugin loaded:

```
> Review the filing at ./client-matters/Doe-I130/ against the i-130-spouse-petition descriptor.
```

The reviewer will:
1. Resolve the descriptor (`descriptors/i-130-spouse-petition.md`).
2. Ask for any case_params the descriptor needs that aren't already known
   (e.g., petitioner status, prior marriages).
3. Estimate cost and warn before running expensive vision passes.
4. Classify each PDF in the folder against the descriptor's required
   components.
5. Evaluate each check and produce a markdown report.

To build a new descriptor:

```
> Help me build a descriptor for a California PC § 1473.7 motion to vacate.
```

## File layout

```
filing-review/
├── README.md                     # this file
├── CHANGELOG.md                  # this skill set's changelog
├── review-filing/
│   ├── SKILL.md
│   └── CHANGELOG.md
├── build-filing-descriptor/
│   ├── SKILL.md
│   └── CHANGELOG.md
├── shared/
│   ├── descriptor-schema.md      # canonical descriptor format spec
│   └── checks/
│       ├── caption_consistency.yaml
│       ├── name_consistency.yaml
│       └── signature_block_completeness.yaml
└── descriptors/
    ├── i-130-spouse-petition.md
    ├── ca-pc-1538.5-motion-to-suppress.md
    └── cacd-civil-complaint.md
```

## Status

| Component | Version | Status |
|---|---|---|
| `review-filing` | 0.1.0 | Alpha — vision evaluation mode only |
| `build-filing-descriptor` | 0.1.0 | Alpha — interview flow drafted, not battle-tested |
| Descriptor schema | 0.1 | Draft; expect breaking changes |
| Named-check library | seed | 3 entries; will grow with each new descriptor |
| Claim-element library | empty | Planned for v0.2 |

See [CHANGELOG.md](CHANGELOG.md) for full history.

## License & attribution

MIT. See [LICENSE](../../LICENSE) in the repo root. Copyright in this skill
set is retained by its author(s) — see the YAML `author` fields and the
Git history.
