# ElPato Legal Skills

> ## ⚠️ ALPHA — ACTIVELY DEVELOPED — NOT VERIFIED TO WORK
>
> **This repository is an alpha. Every skill in it is in active development
> and has not been independently confirmed to produce correct results.**
> Outputs may be wrong, incomplete, or misleading. Do not rely on any
> output without close attorney review, and do not file anything based on
> a skill's output without independently verifying it. Behaviors, file
> formats, descriptor schemas, and skill interfaces can change without
> notice between versions.
>
> If you use a skill on a real matter, treat its output as a junior
> associate's first-pass draft on a bad day — useful as a starting point,
> definitely not the work product.

Community legal skills for **immigration, criminal defense, family law, and civil litigation** — built by practitioners for practitioners.

This registry fills a gap in the [claude-for-legal](https://github.com/anthropics/claude-for-legal) ecosystem: practice-area skills for the areas that weren't covered at launch. Every skill is a draft-for-attorney-review tool, not a legal conclusion engine.

## Practice areas covered

- Immigration (affirmative: asylum, SIJS, VAWA, U/T visa; removal defense; bond)
- Criminal defense (DUI, PCR, expungement)
- Family law (protective orders, custody, dissolution)
- Civil litigation (state and federal)

## Add this registry

In Claude Code:

```
/legal-builder-hub:registry-browser
```

Then add: `https://github.com/ElPatoLegal/legal-skills`

Or edit your allowlist directly:

```yaml
# ~/.claude/plugins/config/claude-for-legal/legal-builder-hub/allowlist.yaml
registries:
  - https://github.com/ElPatoLegal/legal-skills
publishers:
  - ElPatoLegal
```

## Skills

| Skill | Practice area | Status |
|---|---|---|
| `sort-scans` | Multi | Alpha — OCR, identify, name, and file scanned documents into client folders |
| `filing-review/review-filing` | Multi | Alpha — review a filing for completeness and compliance against a descriptor |
| `filing-review/build-filing-descriptor` | Multi | Alpha — build or edit the descriptors used by `review-filing` |

See [CHANGELOG.md](CHANGELOG.md) for a repo-wide history of skill additions and changes; each skill folder also has its own changelog.

## Contributing

Skills are plain-text SKILL.md files. See [CONTRIBUTING.md](CONTRIBUTING.md) for the format and design framework. Practitioners welcome — you don't need to be a developer.

## License & Disclaimer

**License.** This project is licensed under the MIT License. See [LICENSE](LICENSE) for the full text. Contributors retain copyright in their individual skills; the project-level license covers distribution and use.

**No attorney-client relationship.** Use of this repository, any skill in it, or any output produced by a skill does not create an attorney-client relationship with the author or with any contributor.

**Drafts, not advice.** Every output from every skill is an AI-assisted draft intended for review by a licensed attorney. Nothing in this repository constitutes legal advice. Do not rely on any output without independent attorney review.

**Jurisdiction-dependent.** Law varies by jurisdiction and changes over time. Skills declare a target jurisdiction and a `last_verified` date, but it is the user's responsibility to verify that any output is current and correct for the relevant jurisdiction before relying on it or filing it.

**AS IS, no warranty.** The software is provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement, as set out in the MIT License.
