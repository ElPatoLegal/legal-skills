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
author: Your Name (or firm, or "anonymous")
last_verified: YYYY-MM-DD
freshness_window: 6 months
license: MIT
---

> Licensed under the MIT License. See LICENSE in the repo root.
> Copyright in this skill is retained by its author(s) — see the YAML
> `author` field above and this file's Git history.
>
> [AI-ASSISTED DRAFT — requires attorney review. Not legal advice.
> No attorney-client relationship is created by use of this skill.]

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

## License of Contributions

By submitting a pull request, you agree that your contribution is licensed under the MIT License — the same license that covers this project. You also represent that you have the right to license the contribution under these terms (i.e., the contribution is your original work or is otherwise properly licensed for this purpose).

You retain copyright in your contribution. The repo-level MIT License governs distribution and use; it does not transfer copyright to the maintainer or to anyone else. Identify yourself in your SKILL.md's YAML `author` field if you'd like attribution to live in the skill file itself; the Git history is the secondary record either way.
