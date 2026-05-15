---
name: cacd-civil-complaint
description: Federal civil complaint filed in the US District Court, Central District of California — checks FRCP Rules 8, 9, 10, 11 and CACD Local Rules.
jurisdiction: federal (US District Court, C.D. Cal.)
schema: 0.1
evaluation_mode: vision
default_severity: warn
forms_supported:
  - {id: civil_cover_sheet, cite: "CACD Form CV-71"}
  - {id: notice_of_interested_parties, cite: "CACD Form CV-30; L.R. 7.1-1"}
  - {id: summons, cite: "AO 440"}
  - {id: corporate_disclosure, cite: "FRCP 7.1"}
case_params:
  - {key: claim_types, type: list[enum],
     values: [negligence, breach_of_contract, fraud, civil_rights_1983,
              employment_discrimination, fdcpa, lanham_act, copyright,
              trademark, patent, securities, antitrust, other],
     notes: "Drives per-claim element checks. List every cause of action pled."}
  - {key: jurisdictional_basis, type: enum,
     values: [federal_question, diversity, supplemental, removal]}
  - {key: amount_in_controversy, type: number, optional: true,
     required_when: "jurisdictional_basis == diversity"}
  - {key: related_cases_exist, type: bool, default: false}
  - {key: corporate_party_present, type: bool, default: false}
  - {key: pro_hac_vice_counsel, type: bool, default: false}
last_verified: 2026-05-15
freshness_window: 12 months
author: Patrick Kolasinski
license: MIT
---

> Licensed under the MIT License. See LICENSE in the repo root.
> Copyright in this descriptor is retained by its author(s) — see the
> YAML `author` field above and this file's Git history.
>
> [AI-ASSISTED DRAFT — requires attorney review. Not legal advice.
> No attorney-client relationship is created by use of this descriptor.]

# CACD Civil Complaint — Initial Filing Package

## Required components

```yaml
- pleading: {id: complaint, severity: block}
- form:     {id: civil_cover_sheet, severity: block,
             notes: "CACD Form CV-71."}
- form:     {id: summons, severity: block,
             notes: "AO 440, presented electronically via CM/ECF for clerk issuance."}
- form:     {id: notice_of_interested_parties, severity: block,
             notes: "CACD Form CV-30. Per L.R. 7.1-1, filed with first appearance."}
- form:     {id: corporate_disclosure_statement,
             required_when: "corporate_party_present == true",
             severity: block,
             notes: "FRCP 7.1; nongovernmental corporate party must identify any parent corporation and any publicly held corp owning 10%+ of its stock."}
- pleading: {id: notice_of_related_cases,
             required_when: "related_cases_exist == true",
             severity: block,
             notes: "L.R. 83-1.3.1"}
- exhibit:  {id: filing_fee_or_ifp_application, severity: block,
             accepts: [paid_via_PACER, ifp_application_form_AO_239]}
- pleading: {id: pro_hac_vice_application,
             required_when: "pro_hac_vice_counsel == true",
             severity: block,
             notes: "L.R. 83-2.1.3"}
```

## Per-component checks

### complaint — CACD format compliance (L.R. 11-3)

```yaml
- {label: "Proportionally spaced font ≥ 14-point throughout body (L.R. 11-3.1.1)",
   predicate: font_size_measurement,
   params: {min_pt: 14, scope: body},
   severity: block}
- {label: "Line numbers on left margin (L.R. 11-3)",
   predicate: line_numbers_present, severity: block}
- {label: "Double-spaced (L.R. 11-3)",
   predicate: field_present, severity: warn}
- {label: "Page numbers on every page",
   predicate: field_present, severity: warn}
- {label: "Footer with case number on each page after first (L.R. 11-3)",
   predicate: field_present, severity: warn}
```

### complaint — caption page (L.R. 11-3.8 / FRCP 10(a))

```yaml
- {label: "Top-left attorney info block: name, bar #, firm, address, phone, email, role (L.R. 11-3.8(a))",
   predicate: field_present, severity: block}
- {label: "Court title centered: 'UNITED STATES DISTRICT COURT — CENTRAL DISTRICT OF CALIFORNIA'",
   predicate: field_present, severity: block}
- {label: "Parties listed left of center; case number blank or assigned right of center (FRCP 10(a))",
   predicate: field_present, severity: block}
- {label: "Document title below case number area: 'COMPLAINT FOR [causes of action]; DEMAND FOR JURY TRIAL'",
   rule: "the caption page includes a document title that names the causes of action and (if jury trial is sought) the jury demand",
   severity: warn,
   notes: "Jury demand may also appear as separate notation per FRCP 38."}
```

### complaint — FRCP Rule 8(a) requirements

```yaml
- {label: "Short and plain statement of grounds for jurisdiction (FRCP 8(a)(1))",
   rule: "the complaint contains a short and plain statement of the grounds for the court's jurisdiction matching case_params.jurisdictional_basis. For diversity: citizenship of every party and amount in controversy > $75,000. For federal question: cites the specific federal statute or constitutional provision conferring jurisdiction.",
   severity: block}
- {label: "Short and plain statement of the claim showing entitled to relief (FRCP 8(a)(2))",
   rule: "the complaint contains a short and plain statement of the claim showing the pleader is entitled to relief — facts, not just legal conclusions (Twombly/Iqbal plausibility)",
   severity: block}
- {label: "Demand for relief sought (FRCP 8(a)(3))",
   rule: "the complaint includes a prayer for relief; may include alternative forms of relief",
   severity: block}
- {label: "Allegations are simple, concise, and direct (FRCP 8(d)(1))",
   rule: "no paragraph rambles more than ~6 lines; no conclusory recitation of every element without supporting facts",
   severity: warn}
```

### complaint — FRCP Rule 10 form

```yaml
- {label: "Numbered paragraphs, each limited to a single set of circumstances (FRCP 10(b))",
   predicate: field_present, severity: block}
- {label: "Each cause of action pled in a separate, labeled count (FRCP 10(b))",
   rule: "each cause of action listed in case_params.claim_types appears in a separately labeled count in the complaint",
   severity: warn}
- {label: "All parties named in the caption (FRCP 10(a))",
   rule: "every party referenced anywhere in the body of the complaint appears in the caption, and vice versa",
   severity: block}
```

### complaint — FRCP Rule 11(a) signature

```yaml
- {label: "Signed by attorney of record — name, address, email, telephone (FRCP 11(a))",
   predicate: signature_present, severity: block}
- {label: "California Bar number present (CACD practice)",
   predicate: field_present, severity: warn}
```

### complaint — per-claim element checks

```yaml
- include: claim_elements_check
  with:
    claim_type: "{{ each in case_params.claim_types }}"
    locator: "the count alleging this claim in the complaint"
  override:
    severity: block
```

> Note: `claim_elements_check` resolves against `shared/claims/<claim_type>.yaml`.
> The `shared/claims/` library is not shipped in alpha v0.1; the reviewer falls
> back to LLM general knowledge of claim elements until library entries exist.

### complaint — FRCP Rule 9(b) heightened pleading (conditional)

```yaml
- include: rule_9b_particularity
  required_when: "'fraud' in case_params.claim_types"
  with:
    locator: "the count(s) alleging fraud"
  override:
    severity: block
```

> Note: `rule_9b_particularity` is not yet a shared check entry in alpha v0.1;
> the reviewer falls back to evaluating the rule from context. The check verifies
> that fraud is pled with particularity — the who, what, when, where, and how.

### civil_cover_sheet (CV-71)

```yaml
- {label: "Plaintiff(s) and defendant(s) match complaint caption",
   predicate: field_present, severity: block}
- {label: "Basis of jurisdiction matches case_params.jurisdictional_basis",
   predicate: field_present, severity: block}
- {label: "County of residence of first listed plaintiff and defendant",
   predicate: field_present, severity: warn}
- {label: "Nature of suit code", predicate: field_present, severity: warn}
- {label: "Origin code (1 = original proceeding)",
   predicate: field_present, severity: warn}
- {label: "Attorney signature + date (reverse side if printed)",
   predicate: signature_present, severity: warn}
```

### notice_of_interested_parties (CV-30)

```yaml
- {label: "Caption matches complaint", predicate: field_present, severity: block}
- {label: "All parties to the action listed",
   predicate: field_present, severity: block}
- {label: "All other persons/entities with a pecuniary interest listed (or affirmative statement that none exist)",
   rule: "the notice lists every person/entity with a pecuniary interest in the outcome, OR affirmatively states that no such persons/entities exist",
   severity: block}
- {label: "Attorney signature", predicate: signature_present, severity: block}
```

### summons (AO 440)

```yaml
- {label: "Defendant name(s) and address(es)",
   predicate: field_present, severity: block}
- {label: "Plaintiff's attorney info block",
   predicate: field_present, severity: block}
- {label: "Court name", predicate: field_present, severity: block}
- {label: "Case number field (may be blank pre-issuance)",
   predicate: field_present, severity: info}
```

## Cross-document checks

```yaml
- include: caption_consistency
  with:
    docs: [complaint, civil_cover_sheet, notice_of_interested_parties,
           summons, corporate_disclosure_statement, notice_of_related_cases]

- party_lists_match_exactly:
    sources:
      - {doc: complaint, locator: "caption party list"}
      - {doc: civil_cover_sheet, locator: "plaintiffs + defendants section"}
      - {doc: notice_of_interested_parties, locator: "parties list"}
      - {doc: summons, locator: "defendants listed"}
    predicate: party_lists_match_exactly
    severity: block
    notes: "CV-71 box-checking quirks aside, party names must be character-identical to the complaint caption."

- jurisdictional_basis_consistency:
    sources:
      - {doc: complaint, locator: "jurisdictional allegations"}
      - {doc: civil_cover_sheet, locator: "Basis of Jurisdiction section"}
      - {key: case_params.jurisdictional_basis}
    rule: "the basis of jurisdiction selected on the CV-71 matches the jurisdictional allegations in the complaint and case_params.jurisdictional_basis"
    severity: block

- amount_in_controversy_consistency:
    required_when: "jurisdictional_basis == diversity"
    sources:
      - {doc: complaint, locator: "amount in controversy allegation"}
      - {doc: civil_cover_sheet, locator: "Demand $"}
    predicate: amounts_match_or_complaint_states_exceeds_threshold
    severity: block

- include: signature_block_completeness
  with:
    docs: [complaint, notice_of_interested_parties, notice_of_related_cases]
    require: [signature, printed_name, bar_number, address, phone, email, date]
```

## Conditional / contextual rules (free-form, LLM-evaluated)

- For diversity jurisdiction, the complaint must allege the citizenship of every party. For corporate parties, allege both state of incorporation and principal place of business per 28 U.S.C. § 1332(c)(1). The amount in controversy must exceed $75,000 exclusive of interest and costs. [severity: block]
- For federal question jurisdiction, the complaint must identify the specific federal statute or constitutional provision conferring jurisdiction in the body of the pleading (28 U.S.C. § 1331 is rarely sufficient on its own). [severity: block]
- A defendant named in the caption but with no substantive allegations against them is a red flag. Flag any defendant who appears in the caption but is never referenced in any count. [severity: warn]
- A count alleging a state-law claim alongside federal-question claims should affirmatively invoke supplemental jurisdiction (28 U.S.C. § 1367). [severity: warn]
- The complaint should include a separate "Demand for Jury Trial" notation (per FRCP 38) if jury trial is desired. Failure to demand within 14 days of service of the last pleading directed to the issue forfeits the right. [severity: warn]
- For pro hac vice counsel, designate local counsel admitted in the C.D. Cal. (L.R. 83-2.1.3.4). [severity: block]

## Assembly order

CACD e-filing presents these as separate docket events rather than a single bound package. The reviewer checks they're all present in the new-case opening:

1. Complaint (main document)
2. Civil Cover Sheet (CV-71) — as attachment to complaint or separate event
3. Summons (AO 440) — separate event
4. Notice of Interested Parties (CV-30) — separate event
5. Corporate Disclosure Statement (if applicable) — separate event
6. Notice of Related Cases (if applicable) — separate event
7. Filing fee paid or IFP application — case opening event
8. Pro hac vice application(s) if any — separate event
9. Application(s) for admission as local counsel if any

## Filing destination

US District Court, Central District of California. E-filed via CM/ECF. Case opens in the division corresponding to the county of plaintiff's residence (Western — Los Angeles; Southern — Santa Ana; Eastern — Riverside) unless a different division is required by the cause of action.

## Fee

Current filing fee per 28 U.S.C. § 1914 — **[VERIFY]** at https://www.uscourts.gov/services-forms/fees/district-court-miscellaneous-fee-schedule before filing.
