# Filing-Review Status (v0.1.0 alpha)

This document is the honest inventory of what is currently specified in
the two SKILL.md files vs. what is left implicit and would have to be
improvised at runtime. It is the companion to [TESTING.md](TESTING.md):
that doc plans how we verify the skills against a synthetic filing; this
doc is what they are being verified against.

## How to read this

A "skill" in this repository is a Markdown instruction set that an LLM
reads and follows. There is no compiled binary, no service, no
deterministic runtime — only prose instructions and conventional file
layout. "Wired" here therefore means *the instructions are concrete
enough that a competent LLM should execute them the same way each time*.
It does not mean executable code exists.

The categories used below:

- **Wired** — the instruction is concrete, the inputs are specified,
  the output is specified, and there is little for the LLM to invent.
- **Partial** — described, but with material gaps the LLM has to fill in
  (e.g., a step references "filename heuristics" without defining them).
- **Strawman** — the step is named and given a few lines of prose, but
  the actual mechanics are left to the LLM to invent at runtime.
- **Deferred** — explicitly out of scope for alpha; SKILL.md says so.

The status assessments below are based on a read of both SKILL.md files
on 2026-05-15. They have not been validated against an end-to-end run on
any filing.

---

## review-filing

### Invocation UX

Specified in SKILL.md: the attorney triggers the skill conversationally
("review this filing," "audit the I-130 package," "compliance check
against [descriptor]"). The skill expects two inputs:

- `filing_path` — a PDF or folder of PDFs.
- `descriptor` — a descriptor name (e.g., `i-130-spouse-petition`) or
  path to a `.md` file.
- `case_params` — optional dict; missing required params are prompted
  during execution.

**What is not specified:**

- Whether the skill should confirm `filing_path` resolution before
  starting (e.g., echo back "I see N PDFs at this path; proceed?").
- Whether trigger phrases like "review the filing" alone (without a
  named descriptor) should ask the attorney which descriptor to use, or
  refuse, or guess.
- Whether the attorney can pause the run partway through (e.g., after
  classification, before evaluation) to correct a misclassification.

### File-layout assumptions

Specified:

- Descriptor lookup order: explicit path → `./descriptors/<name>.md`
  in the working directory (firm-private override) → the shipped
  `skills/filing-review/descriptors/<name>.md`.
- Shared checks at `skills/filing-review/shared/checks/<name>.yaml`.
- Output report at `<filing_path>/.review-reports/<descriptor>-<ISO>.md`,
  or alongside the PDF for a single-file filing.

**What is not specified:**

- What "the working directory" means when the skill runs inside a Claude
  session whose CWD is the user's repo, the user's home, a client-matter
  folder, or `/tmp`. The lookup is described in the abstract but the
  concrete cwd-resolution rule is not.
- What happens when the same descriptor name exists at both the working
  directory and the shipped location and they differ (firm-private wins,
  per the lookup order, but is this surfaced to the attorney?).
- Whether the `.review-reports/` directory should be `.gitignore`d by
  convention.

### Re-run behavior

Specified:

- "No persistent caching between runs. Re-running on the same filing
  re-evaluates every check." (review-filing/SKILL.md, Limitations.)

**What is not specified:**

- Whether re-runs overwrite the prior report, append, or write a new
  timestamped file. The output-location convention includes
  `<ISO-date>`, suggesting per-day uniqueness only — same-day re-runs
  collide.
- Whether the classification table from a prior run is offered as a
  starting point on a re-run.

### Per-step status

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | Resolve descriptor | Partial | Lookup order is concrete; cwd-resolution and malformed-descriptor handling are not. |
| 2 | Read descriptor | Partial | Markdown reading is fine; `include:` expansion and the one form of templating (`{{ each in case_params.<list> }}`) are described but not stress-tested. |
| 3 | Identify needed case_params | Partial | LLM is expected to scan `required_when:` prose and free-form rules for parameter references. Likely works in simple cases; no guidance for edge cases. |
| 4 | Cost estimate | Strawman | Page count, check count, and a "$0.01–$0.05 per check" heuristic are described. Nothing is computed or validated — the LLM is expected to do arithmetic and present a number. The heuristic itself is invented. |
| 5 | Classify documents to components | Strawman | "Filename heuristics + first-page vision sampling" — neither the heuristics nor the sampling protocol exist. This is the single riskiest step. |
| 6 | Evaluate checks | Strawman | 17 predicates are named in the schema; zero are implemented as code. In alpha, every predicate effectively reduces to "LLM looks at a rendered page and decides." The distinction between `field_present`, `signature_present`, `date_present`, etc. depends entirely on the LLM correctly interpreting the predicate name. |
| 7 | Assemble report | Wired | Output skeleton is fully specified; an LLM can fill it in. |
| 8 | Failure handling | Partial | Three modes are listed. The "predicate not natively implemented → fall back to prose" rule is ambiguous because no predicate is natively implemented; the rule effectively applies to every predicate. |

### Output guardrail

Specified: every report must include the "AI-ASSISTED DRAFT — requires
attorney review. Not legal advice" banner prominently. **Wired.**

### Deferred (out of scope for alpha)

- `evaluation_mode: acroform` — extract values from AcroForm fields directly.
- `evaluation_mode: hybrid` — AcroForm first, fall back to vision.
- `evaluation_mode: fingerprint` — confirmed field-name-to-label map per form edition.
- `shared/claims/` library — claim-element checks fall back to LLM general knowledge.
- Court-day timeliness (judicial calendar, weekend/holiday math).
- Cost optimization (text-extraction-first triage to skip vision).
- Firm-private descriptor override directory beyond the simple cwd-lookup.

---

## build-filing-descriptor

### Invocation UX

Specified in SKILL.md: the attorney triggers the skill conversationally
("build a descriptor for X," "help me write a descriptor," "modify the
I-130 descriptor for [variant]"). The skill expects:

- `filing_name` — free text, becomes basis for the descriptor name + file.
- `jurisdiction` — free text.
- `existing_descriptor` — optional; path or name if editing.
- `sample_filing_path` — optional; used in step 10 to validate.

The skill is described as an 11-step interview taking ~1.5–2.5 hours in
aggregate based on the per-step time estimates.

**What is not specified:**

- **Pacing.** Whether the skill asks one question at a time, batches
  questions per step, or presents a structured form. The "5–10 min"
  framing implies extended conversation but the LLM has no explicit
  pacing rule.
- **Intermediate state display.** Whether the skill shows a running
  YAML draft as it goes, only at the end, or never. The attorney has
  no way to check what is being captured mid-interview unless they ask.
- **Step navigation.** Whether the attorney can go back ("change my
  answer to step 3"), skip forward, or jump out of order.
- **Resume.** Whether a partially-completed interview can be paused and
  resumed across sessions, or whether each interview is single-session.

### Edit-vs-create UX

The skill accepts an `existing_descriptor` input but the interview steps
do not specify how the skill should behave differently when editing:

- Does it skip steps the existing descriptor already answers?
- Does it re-confirm every answer, walking the attorney through each
  step with the current value as the default?
- Does it read the existing descriptor and start by asking "what do you
  want to change?"

Step 11 says "overwrite the source file with the revised content. Show a
diff to the attorney before writing." That nails the *write* step but
leaves the interview-flow-for-editing strawman.

### File-layout assumptions

Specified:

- New community descriptors: `skills/filing-review/descriptors/<name>.md`
  + CHANGELOG entry.
- Firm-private: a path the attorney specifies.
- Edit: overwrite the source.

**What is not specified:**

- **Filename collision.** What happens when `<name>.md` already exists
  and the attorney is creating a new descriptor (not editing).
- **The community-vs-firm-private decision.** SKILL.md says "the skill
  chooses based on context." The actual heuristic is undefined.
- **Library promotion (step 7).** The path for a new `shared/checks/`
  entry is implied but the template for a new check file is only loosely
  described in `shared/descriptor-schema.md` — the build skill is
  expected to produce one without an explicit template.

### Per-step status

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | Identification | Wired | A focused set of well-formed questions. |
| 2 | Case parameters | Partial | Question set is clear; pacing and intermediate display are not. |
| 3 | Required components | Partial | Clear questions; the YAML capture format is the schema's, which is concrete. |
| 4 | Per-component structure checks | Strawman | Mentions "pull the structure from the actual form if possible (ask the attorney to share a sample)." If the attorney shares a sample, the skill is expected to read it — but no protocol for how the read produces field-level checks. |
| 5 | Cross-document checks | Partial | Names 6 cross-checks; the library currently contains 3 (`caption_consistency`, `name_consistency`, `signature_block_completeness`). The skill may offer checks (`identifier_consistency`, `period_coverage`, `factual_consistency`) that don't exist as files. |
| 6 | Free-form contextual rules | Wired | LLM asks, attorney answers, captured as bullets. |
| 7 | Promote one-offs to library | Strawman | The write target is named (`shared/checks/<name>.yaml`); the template format is in `shared/descriptor-schema.md` but the build skill has no explicit checklist for producing a conformant entry. |
| 8 | Assembly order | Wired | Single question, captured as a numbered list. |
| 9 | Filing destination and fee | Wired | Two questions, captured verbatim. |
| 10 | Validate against sample | Strawman | "Invoke the `review-filing` skill on the sample." Cross-skill invocation in the same Claude session is not a defined mechanism — in practice this means Claude switches modes and does what review-filing's SKILL.md says. The handoff has never been tested. |
| 11 | Write descriptor | Partial | Write target rule is clear; community-vs-firm-private heuristic and collision handling are not. |

### Output guardrail

Specified: every produced descriptor carries the standard disclaimer
block, and the skill surfaces in chat that the descriptor is alpha and
should be validated against at least one known-good filing. **Wired.**

### Deferred (out of scope for alpha)

- Structural validation of the produced descriptor against the schema.
- Version control of descriptors beyond what the attorney commits manually.
- Schema-aware autocomplete during the interview (e.g., "this predicate
  doesn't exist, did you mean…").

---

## Cross-cutting unknowns

These are gaps that span both skills.

- **Cross-skill invocation.** build-filing-descriptor step 10 calls
  review-filing. Both skills run in the same Claude session by Claude
  reading SKILL.md and executing instructions. There is no formal
  handoff protocol — the LLM is expected to recognize that it should
  now follow review-filing's SKILL.md, then return to where it was in
  build-filing-descriptor's interview. Untested.
- **The runtime is the LLM.** Every predicate, every classification
  decision, every cost estimate, every report assembly happens inside
  the LLM. There is no Python helper, no compiled tool, no script in
  this repo. The "predicates" are predicate *names* the LLM is expected
  to honor; their semantics live in `shared/descriptor-schema.md` as
  prose definitions, not as code.
- **Vision-only in practice.** Even though three other evaluation modes
  are documented, the alpha falls back to vision for all of them. This
  means every check is a rendered-page + LLM-reasoning pass. Cost
  estimates and runtime are dominated by this.
- **No test fixtures.** There is no `tests/` directory, no synthetic
  filing, no fixture descriptor known to be correct. The first end-to-end
  run will be against material we create for that purpose.

---

## Bottom line

The two skills describe a coherent workflow at the conceptual level.
The most concrete parts are: the descriptor schema, the report skeleton,
the in-skill disclaimer banners, and the file-layout conventions. The
least concrete parts — and the parts most likely to surface issues in
testing — are document classification, predicate evaluation under a
vision-only runtime, the cost estimate, the form-reading step in
build-filing-descriptor, and the cross-skill invocation in step 10.

TESTING.md plans how to drive these from concept to verified behavior.
