---
name: i-130-spouse-petition
description: USCIS Form I-130, Petition for Alien Relative — spouse beneficiary
jurisdiction: federal (USCIS)
schema: 0.1
evaluation_mode: vision
default_severity: warn
forms_supported:
  - {id: i-130,  editions: ["04/01/24", "10/05/23"]}
  - {id: i-130a, editions: ["04/01/24"]}
case_params:
  - {key: petitioner_status, type: enum, values: [USC, LPR]}
  - {key: prior_marriages_petitioner, type: int, default: 0}
  - {key: prior_marriages_beneficiary, type: int, default: 0}
  - {key: filing_mode, type: enum, values: [paper_lockbox, online_myUSCIS]}
last_verified: 2026-05-15
freshness_window: 6 months
author: Patrick Kolasinski
license: MIT
---

> Licensed under the MIT License. See LICENSE in the repo root.
> Copyright in this descriptor is retained by its author(s) — see the
> YAML `author` field above and this file's Git history.
>
> [AI-ASSISTED DRAFT — requires attorney review. Not legal advice.
> No attorney-client relationship is created by use of this descriptor.]

# I-130 — Petition for Alien Relative (Spouse)

## Required components

```yaml
- form:    {id: i-130,  severity: block}
- form:    {id: i-130a, severity: block}
- exhibit: {id: petitioner_proof_of_status, severity: block,
            accepts_when_USC: [us_passport_bio_page, naturalization_certificate, us_birth_certificate],
            accepts_when_LPR: [green_card_both_sides, foreign_passport_with_i551_stamp]}
- exhibit: {id: marriage_certificate, severity: block,
            notes: "Certified copy + English translation if originally non-English."}
- exhibit: {id: petitioner_divorce_decrees,
            required_when: "prior_marriages_petitioner > 0",
            severity: block}
- exhibit: {id: beneficiary_divorce_decrees,
            required_when: "prior_marriages_beneficiary > 0",
            severity: block}
- exhibit: {id: filing_fee_or_g1450,
            required_when: "filing_mode == paper_lockbox",
            accepts: [personal_check, money_order, cashiers_check, form_g1450],
            severity: block}
- exhibit: {id: cover_letter_with_toc, severity: info}
```

## Per-component checks

### i-130 (edition 04/01/24)

```yaml
- {label: "Part 1, Item 1 — Petitioner family name + given name",
   predicate: field_present, severity: block}
- {label: "Part 1, Item 8 — Mailing address complete",
   predicate: field_present, severity: block}
- {label: "Part 2, Item 1 — Spouse box checked",
   predicate: field_present, severity: block}
- {label: "Part 2, Items 6/7/11 — Beneficiary name + DOB",
   predicate: field_present, severity: block}
- {label: "Part 4, Item 3 — Date of current marriage",
   predicate: date_present, severity: block}
- {label: "Part 4 — Prior spouses listed",
   predicate: field_present,
   required_when: "prior_marriages_petitioner > 0",
   severity: block}
- {label: "Part 9 — Petitioner signature (wet, blue ink preferred for lockbox)",
   predicate: signature_present, severity: block}
- {label: "Part 9 — Date of signature",
   predicate: date_present, severity: block}
```

### i-130a (edition 04/01/24)

```yaml
- {label: "Part 2 — Address history last 5 years, no gaps",
   rule: "Part 2 lists every address the beneficiary has had in the past 5 years, with no unexplained gaps and matching date ranges (end of one period = start of next)",
   severity: block}
- {label: "Part 3 — Employment history last 5 years, no gaps",
   rule: "Part 3 lists every employer (or unemployment period) the beneficiary has had in the past 5 years, with no unexplained gaps",
   severity: block}
- {label: "Part 6 — Beneficiary signature",
   predicate: signature_present,
   severity: block,
   notes: "If beneficiary is abroad and unable to sign, Part 6 may be left blank — verify against current instructions."}
```

## Cross-document checks

```yaml
- include: name_consistency
  with:
    docs: [i-130, petitioner_proof_of_status, marriage_certificate]
    party: petitioner
    normalization: {middle_optional: true, suffix_optional: true, transliteration_tolerant: true}
  override:
    severity: warn

- include: name_consistency
  with:
    docs: [i-130, i-130a, marriage_certificate]
    party: beneficiary
    normalization: {middle_optional: true, suffix_optional: true, transliteration_tolerant: true}
  override:
    severity: warn

- beneficiary_dob_consistency:
    sources:
      - {doc: i-130,  locator: "Part 2 Item 11 DOB"}
      - {doc: i-130a, locator: "Part 1 DOB"}
    predicate: dates_exact
    severity: block

- marriage_date_consistency:
    sources:
      - {doc: i-130, locator: "Part 4 Item 3 date of current marriage"}
      - {doc: marriage_certificate, locator: "date of marriage"}
    predicate: dates_exact
    severity: block

- place_of_marriage_consistency:
    sources:
      - {doc: i-130, locator: "Part 4 Item 2 place of current marriage"}
      - {doc: marriage_certificate, locator: "place of marriage / issuing jurisdiction"}
    predicate: places_match
    severity: warn

- petitioner_anumber_consistency:
    required_when: "petitioner_status == LPR"
    sources:
      - {doc: i-130, locator: "Petitioner A-Number field"}
      - {doc: petitioner_proof_of_status, locator: "A-Number on green card / I-551 stamp"}
    predicate: identifiers_exact
    severity: block

- proof_of_status_to_petition_consistency:
    sources:
      - {doc: petitioner_proof_of_status, locator: "DOB, place of birth, country of birth"}
      - {doc: i-130, locator: "Part 1 petitioner identification fields"}
    rule: "DOB, place of birth, and country of birth on the proof of status do not conflict with the corresponding I-130 fields"
    severity: block

- divorce_decree_party_consistency:
    required_when: "prior_marriages_petitioner > 0 OR prior_marriages_beneficiary > 0"
    sources:
      - {doc: petitioner_divorce_decrees}
      - {doc: beneficiary_divorce_decrees}
      - {doc: i-130, locator: "petitioner + beneficiary names; prior spouse names if listed"}
    rule: "each decree names the relevant petitioner or beneficiary; prior spouse names match Part 4 prior-spouses entries if listed"
    severity: warn

- include: period_coverage
  with:
    source: {doc: i-130a, locator: "Part 2 address history"}
    target_window: "5 years before filing_date"
    allow_gaps_up_to_days: 0
  override:
    severity: block

- include: period_coverage
  with:
    source: {doc: i-130a, locator: "Part 3 employment history"}
    target_window: "5 years before filing_date"
    allow_gaps_up_to_days: 0
  override:
    severity: block
```

## Conditional / contextual rules (free-form, LLM-evaluated)

- Petitioner divorce decree dates must precede the current marriage date; flag any inversion. [severity: block]
- If either spouse changed names by marriage, the marriage certificate must reference both names — otherwise a separate name-change order is needed. [severity: warn]
- LPR petitioner with a prior pending I-130 for a spouse: flag (only one at a time). [severity: warn]
- If the detected form edition is not in `forms_supported.editions`, downgrade all per-form checks to `warn` and surface a "verify edition acceptable at time of filing" note. USCIS publishes a grace period after each new edition.

## Assembly order

1. Cover letter / TOC
2. G-28 (if attorney-represented)
3. I-130 (signed)
4. I-130A (signed)
5. Filing fee or G-1450 (paper only)
6. Petitioner proof of status
7. Marriage certificate
8. Divorce decrees (petitioner, then beneficiary, if any)
9. Evidence of bona fide marriage (joint financial accounts, lease, photos, affidavits)

## Filing destination

- **Paper:** USCIS Lockbox. Address varies by petitioner's state of residence and whether a concurrent I-485 is filed. **VERIFY** against the current USCIS direct filing addresses page before filing.
- **Online:** myUSCIS for eligible filers (no paper fee item required).

## Fee

$675 paper / $625 online as of 2026-04-12. **[VERIFY]** before filing — USCIS adjusts fees.
