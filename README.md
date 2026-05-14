# ElPato Legal Skills

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
| `sort-scans` | Multi | OCR, identify, name, and file scanned documents into client folders |

## Contributing

Skills are plain-text SKILL.md files. See [CONTRIBUTING.md](CONTRIBUTING.md) for the format and design framework. Practitioners welcome — you don't need to be a developer.

## License

MIT. Every output from every skill is a draft for attorney review — not legal advice.
