# Filing-Review Testing Plan (v0.1.0 alpha)

This plan walks the pipeline in order: generator first, validator
second, defect injection third, round-trip last. The goal is to verify
that the two skills execute their *specified* workflow without getting
confused — not to verify that the reports are substantively correct on
a real filing. Substantive correctness is a later milestone.

Read [STATUS.md](STATUS.md) before this document. It enumerates which
steps in each SKILL.md are concrete and which are strawman; the testing
stages below are organized to surface failures in the strawman parts
first, because those are the most likely to break.

## Approach

The pipeline:

```
build-filing-descriptor (interview)
        ↓ produces
   descriptor (.md)
        ↓ consumed by
review-filing (evaluation)
        ↓ produces
        report (.md)
```

We test stage by stage. A stage failing means we fix the SKILL.md (or
the schema, or the named-check library) before moving on. We do not
queue up multiple stage failures.

Each stage has explicit **pass criteria** and a list of **likely
failure modes** drawn from STATUS.md. If a stage passes despite a
known strawman concern, that is information worth capturing in
STATUS.md.

## What "pass" means in this round

A passing stage means: *the skill executes its specified workflow
without getting confused and produces output of the documented shape.*
A passing stage does **not** mean the output is correct on a real
filing. That bar is intentionally deferred. The alpha goal is "the
machine works end to end." Correctness on real filings is the next
milestone.

## Test fixture choice

Use **I-130 spouse petition** as the first pipeline target. Rationale:

- It is the most concrete shipped descriptor.
- It mixes forms (I-130, I-130A) with pleadings/exhibits (proof of
  status, marriage certificate, divorce decrees if any).
- USCIS forms are public domain, so synthetic samples are easy to
  produce without privacy concerns.
- The form fields are mostly textual, so vision-only evaluation is a
  realistic test (no unusual layout).

Synthetic fixtures we'll need:

- A "clean" synthetic I-130 package: filled I-130, filled I-130A,
  fake-but-plausible marriage certificate image, US passport bio
  page mock, and a cover letter with TOC. All clearly marked
  `SAMPLE — NOT A REAL FILING`.
- A "defective" version derived from the clean one: caption mismatch
  on the cover letter, missing I-130A, unsigned I-130, beneficiary DOB
  inconsistent between I-130 and I-130A.

These fixtures should live outside the public repo (a fixtures folder
in the private mirror or local-only). They do not need to be committed
to this repo.

---

## Stage 1 — build-filing-descriptor UX smoke

**Goal:** Walk the interview end to end with a fresh Claude session.
Observe whether it executes the 11 steps coherently.

**Setup:** Fresh Claude session with this plugin loaded. No existing
descriptor context. Trigger: *"Help me build a descriptor for the I-589
asylum application."* (Deliberately a filing type with no shipped
descriptor, so the LLM cannot fall back on a reference.)

**Pass criteria:**

- All 11 steps execute in order. None are skipped silently. None are
  conflated.
- Question pacing is usable — the attorney is not asked 20 questions in
  one turn, and is not stuck in a one-question-per-turn loop for an
  hour either.
- The attorney can see what is being captured (running YAML draft, or
  end-of-step summary) without having to ask.
- The skill correctly distinguishes between case_params (step 2) and
  per-component checks (step 4). These are easy to conflate.
- The interview reaches step 11 and writes a file.

**Likely failure modes (from STATUS.md):**

- *Pacing*: skill blasts through with batched questions, or stalls in
  one-question-per-turn mode. Pacing is unspecified.
- *Intermediate state*: attorney cannot see the in-progress descriptor.
- *Step 4 form reading*: skill asks for a sample I-589 and then has no
  protocol for extracting fields from it.
- *Step 5 library walk*: skill offers `identifier_consistency` or
  `period_coverage` as if they exist; both are referenced in
  build-filing-descriptor/SKILL.md but neither is a file in
  `shared/checks/`.
- *Step 7 library promotion*: skill offers to promote a one-off check
  but produces a malformed `.yaml` entry because the file template is
  not pinned down.

**Observation log:** Capture, for each step, whether it executed,
whether pacing was usable, and whether the attorney would have known
what was being captured. Update STATUS.md with anything that turns out
to be wired or strawman differently than expected.

---

## Stage 2 — Descriptor schema conformance

**Goal:** The descriptor produced by Stage 1 actually conforms to the
schema in `shared/descriptor-schema.md`.

**Setup:** Take the descriptor file from Stage 1 and manually check it
against the schema. This is a static check; no Claude session needed.

**Pass criteria:**

- YAML frontmatter parses as YAML.
- All required frontmatter fields present (`name`, `description`,
  `jurisdiction`, `schema`, `last_verified`, `freshness_window`,
  `author`, `license`).
- `schema: 0.1` declared.
- All H2 body sections present in the conventional order.
- Disclaimer block present after frontmatter.
- Every `include:` reference resolves to a file in `shared/checks/`.
- Every `predicate:` name appears in the predicate table in the schema.
- Every `required_when:` expression references a case_param the
  descriptor declares.
- Every fan-out (`{{ each in case_params.<list> }}`) references a
  case_param declared as `list[...]`.

**Likely failure modes:**

- Frontmatter fields missing or out of order.
- `include:` references to library entries that don't exist.
- Predicate names that don't appear in the schema's table.
- `required_when:` referencing case_params that were renamed mid-interview.

**If this fails:** The fix is in the build skill, not the descriptor.
Tighten the relevant step's instructions and re-run Stage 1.

---

## Stage 3 — review-filing UX smoke

**Goal:** Drive review-filing with the existing `i-130-spouse-petition`
descriptor and the clean synthetic I-130 package. (Switch from the
Stage 1 descriptor to the shipped one here, because we now want to
test the validator, not the validator-plus-a-Stage-1-descriptor.)

**Setup:** Fresh Claude session. Place the clean synthetic I-130
package at a working directory. Trigger: *"Review the filing at
./fixtures/clean-i130/ against the i-130-spouse-petition descriptor."*

**Pass criteria:**

- Descriptor resolves cleanly via the documented lookup order. The
  skill says which path it resolved from.
- Case_params interview surfaces the four declared params
  (`petitioner_status`, `prior_marriages_petitioner`,
  `prior_marriages_beneficiary`, `filing_mode`) and accepts answers.
- Cost estimate appears before vision work begins. Numbers may be
  invented but should be in a plausible range and clearly labeled as
  estimates.
- Pre-run summary is honest about what will be evaluated: total checks
  after include expansion, total pages.
- The attorney sees a "proceed / no / sample-first" choice.

**Likely failure modes (from STATUS.md):**

- *Lookup ambiguity*: skill picks up a descriptor from an unexpected
  directory and does not say so.
- *Cost estimate*: numbers are wildly off (e.g., $5 for a 20-page
  filing or $0.05 for a 200-page filing) — the heuristic is invented.
- *case_params prompt*: skill asks for params the descriptor doesn't
  declare, or skips params it does declare.
- *Sample-first*: skill doesn't honor the sample-first choice or
  doesn't offer it.

---

## Stage 4 — review-filing produces a report on the clean package

**Goal:** A well-formed report file lands where the SKILL.md says it
will, with the documented sections.

**Setup:** Continue Stage 3, choosing "proceed."

**Pass criteria:**

- Report file exists at `<filing_path>/.review-reports/<descriptor>-<ISO>.md`.
- Report is also printed inline.
- Disclaimer banner is present.
- Header includes filing path, descriptor name + schema version + last_verified, case_params, generated timestamp.
- Summary line with BLOCK / WARN / INFO counts and component identification fraction.
- Document classification table present.
- BLOCK / WARN / INFO sections present (any of them may be empty;
  empty sections should still render with a "none" placeholder).
- Filing destination + fee section surfaced verbatim from the descriptor.
- Re-running on the same day surfaces or handles the filename
  collision (per STATUS.md, behavior is unspecified — observe what
  the LLM chooses).

**Likely failure modes (from STATUS.md):**

- *Classification*: every PDF in the folder is classified as the I-130
  form, or none of them are. Filename heuristics are unspecified.
- *Predicate evaluation*: `signature_present` and `date_present` are
  reported indistinguishably because the LLM treats every predicate
  as "look at the page."
- *Output path*: report ends up next to the PDF instead of in
  `.review-reports/`, or vice versa.
- *Empty sections*: BLOCK / WARN / INFO headers omitted when counts
  are zero rather than rendered with a "(none)" placeholder.

---

## Stage 5 — Defect injection

**Goal:** The report actually catches deliberately introduced defects.

**Setup:** The "defective" synthetic I-130 package. Same trigger as
Stage 3 but pointed at the defective fixture.

**Pass criteria:**

- *Missing component* (no I-130A) is reported under "Missing components"
  with severity `block`.
- *Unsigned form* (no I-130 Part 9 signature) is reported as a block-severity
  per-component check failure.
- *Caption mismatch* on the cover letter is reported if a cross-document
  caption check applies. (For I-130 it might not — this is a forms-based
  filing, not a pleading-stack filing — so note whether the descriptor's
  current cross-doc checks would catch the injected defect at all.)
- *DOB inconsistency between I-130 and I-130A* is reported by the
  beneficiary_dob_consistency check.

**Likely failure modes:**

- False negative: a defect that should be reported is missed. Most likely
  on the classification step if a misclassified document means the check
  was never run against the right pages.
- False positive: clean items reported as defective.
- Severity mis-assignment: a `block` reported as `warn` or vice versa.

**Failure-mode triage:** When a defect is missed, distinguish:
- *Classification fault*: the right check ran against the wrong document.
- *Predicate fault*: the LLM evaluated the predicate incorrectly.
- *Descriptor fault*: the descriptor doesn't actually have a check for
  this defect.

The fix differs for each.

---

## Stage 6 — Round-trip: build skill's step 10 validation

**Goal:** The cross-skill invocation in build-filing-descriptor step 10
actually works.

**Setup:** Fresh Claude session. Trigger build-filing-descriptor for a
new variant of an existing filing type (e.g., I-130 for an LPR
petitioner, which differs from the shipped descriptor's USC-default
phrasing). Provide the clean synthetic I-130 package as
`sample_filing_path`. Walk through to step 10.

**Pass criteria:**

- At step 10, the build skill invokes review-filing on the sample.
- Review-filing produces a report against the just-authored descriptor.
- The build skill reads the report and walks the attorney through
  any false-positive / false-negative / misclassification items.
- After iteration, the build skill returns to step 11 and writes the
  descriptor.

**Likely failure modes (from STATUS.md):**

- *Cross-skill invocation*: the LLM doesn't switch context cleanly.
  Either it tries to evaluate the filing using build skill instructions
  (wrong), or it loses the build-interview state when it switches.
- *Re-entry to step 11*: after the validation walk, the LLM forgets it
  was in step 10 and either skips step 11 or restarts the interview.
- *Sample path resolution*: the skill cannot find the sample at the
  given path, or finds it but can't tell review-filing to use it.

---

## Out of scope for this round

The following are not tested in the alpha pass. They are listed here so
we are explicit about what is not being verified yet.

- **Non-vision evaluation modes** (acroform / hybrid / fingerprint).
  STATUS.md confirms all fall back to vision in alpha.
- **shared/claims/ library.** Not shipped in v0.1.
- **Multi-descriptor sessions** (e.g., reviewing one filing against two
  descriptors in the same run).
- **Persistent caching** across runs.
- **Court-day timeliness** rules.
- **Real (non-synthetic) client filings.** This is a correctness bar,
  not an end-to-end mechanics bar, and is the next milestone.
- **Cost estimate accuracy.** The estimate is presented in Stage 3 but
  not validated against actual model usage.
- **Multi-jurisdiction descriptors.** All shipped descriptors are
  jurisdiction-specific; cross-jurisdiction interaction is not tested.

---

## Test execution rhythm

A pipeline-order pass through Stages 1–6 will take multiple sessions.
The expected rhythm:

1. **Session A:** Stage 1 (build skill UX smoke).
2. **Session B:** Stage 2 review of Stage 1 output. May trigger
   Stage 1 SKILL.md edits and a re-run.
3. **Session C:** Stages 3 + 4 (review-filing on clean fixture).
4. **Session D:** Stage 5 (defect injection).
5. **Session E:** Stage 6 (round trip).

Each session ends with a STATUS.md update reflecting what was learned.
If a stage requires a SKILL.md change, the change is committed before
the next stage runs, so the next stage tests the *current* spec rather
than a moving target.

## Exit criteria for the alpha milestone

The alpha "passes" when:

- All six stages have been executed at least once.
- All `Pass criteria` items are checked or have an explicit, documented
  exception in STATUS.md.
- Open defects are filed (as TODO bullets in STATUS.md or as commits
  scheduled for v0.1.1) rather than silently carried forward.

After that, the next milestone (v0.2) takes on substantive correctness
on real filings, the deferred evaluation modes, and the claims library.
