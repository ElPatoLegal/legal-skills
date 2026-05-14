# Contributing Skills

Skills are plain-text markdown files. Each skill lives in its own folder under `skills/`.

## Structure

```
skills/
└── your-skill-name/
    ├── SKILL.md          # required — the skill itself
    └── references/       # optional — templates, checklists, standing assumptions
        └── *.md
```

## SKILL.md format

```markdown
---
name: your-skill-name
description: "One sentence — what it does and when to use it. Include trigger phrases."
practice_area: immigration | criminal | family | civil-litigation
jurisdiction: federal | [state] | multi-jurisdiction
last_verified: YYYY-MM-DD
freshness_window: 6 months
license: MIT
---

# Skill Title

## Purpose
What this skill does and what it doesn't do.

## Who this is for
...

## Commands / workflow
...

## Output format
...

## Guardrails
Every output must be marked: [AI-ASSISTED DRAFT — requires attorney review]
```

## Design principles

1. **Draft, not conclusion.** Every output is a starting point for attorney review.
2. **Cite sources.** Tag citations by source. Use `[VERIFY: ...]` for anything unverified.
3. **Flag uncertainty.** Use `[UNCERTAIN: ...]` rather than guessing.
4. **Gate consequential actions.** Anything filed, sent, or executed requires explicit confirmation.
5. **Jurisdiction-aware.** State what jurisdiction the skill assumes; flag when it doesn't know.
6. **Freshness.** Declare `last_verified` and `freshness_window` — regulatory content changes.

## Submitting

Open a PR. Include in the PR description:
- What the skill does
- What it doesn't do
- What you tested it on (anonymized)
- Jurisdiction(s) covered
