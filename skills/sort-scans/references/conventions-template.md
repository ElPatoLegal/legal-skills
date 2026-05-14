# Scans Folder Conventions — [YOUR FIRM NAME]

> Naming and sorting rules for the Scans folder.
> Referenced by the sort-scans skill. Update this file when conventions change.
> Copy this file to `conventions.md` and fill in your firm-specific details.

---

## Table of Contents

1. [Golden Rules](#1-golden-rules)
2. [Folder Structure](#2-folder-structure)
3. [Date Prefix Rules](#3-date-prefix-rules)
4. [Document Type Naming Guide](#4-document-type-naming-guide)
   - 4.1 [Receipt Notices (USCIS, BIA, etc.)](#41-receipt-notices-uscis-bia-etc)
   - 4.2 [Government Documents](#42-government-documents)
   - 4.3 [Court Documents](#43-court-documents)
   - 4.4 [Client Correspondence](#44-client-correspondence)
   - 4.5 [Client Files](#45-client-files)
   - 4.6 [IDs, Physical Documents & Cards](#46-ids-physical-documents--cards)
   - 4.7 [Notes](#47-notes)
   - 4.8 [Closed File Contact Sheets](#48-closed-file-contact-sheets)
   - 4.9 [Attorney Personal Documents](#49-attorney-personal-documents)
   - 4.10 [Practice-Area Specific](#410-practice-area-specific)
5. [Unreadable Documents](#5-unreadable-documents)
6. [Edge Cases](#6-edge-cases)
7. [Rename Safety Rules](#7-rename-safety-rules)
8. [Changelog](#8-changelog)

---

## 1. Golden Rules

These two rules override everything else.

**Rule 1: No client names in file names** *(when USE_CLIENT_FOLDERS is true).*
Client identity lives in the folder. The filename describes the document.

```
✓  2026-02-07 I-90 Biometrics.pdf
✗  2026-02-07 I-90 Biometrics - Smith, John.pdf
```

When `USE_CLIENT_FOLDERS` is `false`, client name goes in the filename since
there is no folder to imply it — Rule 1 is suspended.

**Rule 2: Date prefix is the document date, always YYYY-MM-DD.**
Use the date that appears on the document itself.

| Document type | Which date to use |
|---------------|-------------------|
| I-797 notices | Notice date (not priority date, not receipt date) |
| Letters | Date at the top of the letter |
| Handwritten notes | Date written on the page |
| Court filings | Filing date or date on the document |
| Criminal histories / FOIAs | Date on the report or response letter |
| IDs / cards | Issue date if visible, otherwise scan date |
| Any document | The most prominent date identifying when it was created |

**Fallback order when document date is unclear:**
1. Scanner filename prefix (e.g., `20260213_` → `2026-02-13`)
2. File modified date

**Rule 3: Staff names are never client names.**
Staff names are listed in `references/staff-names.txt`. If a staff name appears
prominently on a document (e.g., email inbox owner, addressee), keep looking
for the actual client name in handwritten annotations, the email body, or
elsewhere on the page.

---

## 2. Folder Structure

All sorted files live under `Sorted/`.

**`USE_CLIENT_FOLDERS: true`**

> Set to `false` to put all files flat into `Sorted/` with client name in
> the filename. Useful during practice management migrations or when per-client
> folder organization isn't yet set up. `_No Client/` and `_Unreadable/` still
> function normally when `false`.

When `true` (default):
```
Sorted/
├── Last, First/              ← one folder per client
│   ├── Receipt Notices/      ← immigration notices only (see §4.1)
│   ├── FOIAs/                ← criminal histories, FOIA records (see §4.2)
│   └── [other client files]
├── _No Client/               ← general office docs with no specific client
├── _Unreadable/              ← scans that cannot be read or identified
└── sort-scans.log            ← append-only processing log
```

When `false`:
```
Sorted/
├── [all named files]         ← filename includes client name suffix
├── _No Client/
├── _Unreadable/
└── sort-scans.log
```

**Client folder naming:** `Last, First` — family name first. Include full
compound surnames (e.g., `Barrera Mendoza, Carlos`). For multi-member matters
(e.g., family guardianship), use the family surname as a shared folder.

**`_No Client`** catches:
- General office forms (blank questionnaires, conflict waivers)
- Government bulletins and policy docs not tied to a specific client
- Office administrative docs
- Attorney personal documents

**`_Unreadable`** catches:
- Scans where content cannot be determined after OCR + vision
- Illegible handwritten notes
- OCR failures

---

## 3. Date Prefix Rules

| Priority | Source | When to Use |
|----------|--------|-------------|
| 1 | Document date | The date on the document itself (see Rule 2 table) |
| 2 | Scanner filename prefix | File starts with `YYYYMMDD_` — convert to `YYYY-MM-DD` |
| 3 | File modified date | Last resort only |

Always format as `YYYY-MM-DD`.

---

## 4. Document Type Naming Guide

### 4.1 Receipt Notices (USCIS, BIA, etc.)

*Delete this section if your firm does not handle immigration matters.*

All immigration notices — I-797s, approval letters, denial letters, NOIDs,
biometrics appointments, RFEs, BIA decisions, NVC notices — go in the client's
`Receipt Notices/` subfolder.

**Only immigration agency notices go here.** Physical documents (EAD cards,
green cards, passports) go in the client folder directly (see §4.6).

**No "USCIS" prefix on USCIS notices.** The folder implies the agency.
Other agencies (BIA, NVC, etc.) DO get their agency name in the filename.

```
[date] [Application] [Notice Type].pdf      ← USCIS notices
[date] [Agency] [Description].pdf           ← non-USCIS (BIA, NVC, etc.)
```

**USCIS notice types:** Receipt, Biometrics, Payment Receipt, Transfer Notice,
Approval, Denial, NOID, Decision, RFE, Rejection

**Common application types:** I-90, I-130, I-131, I-360, I-485, I-539, I-589,
I-601, I-751, I-765, I-821, I-918, N-400

**How to determine notice type:** Read the "NOTICE TYPE" field on the I-797C.
Read the "CASE TYPE" field for the application type. Do not call something
"Receipt Notice" — name it by application + notice type.

**Examples:**
```
2026-02-07 I-90 Biometrics.pdf
2026-02-13 I-130 Receipt.pdf
2026-01-16 I-485 Payment Receipt.pdf
2017-09-14 I-765 Approval.pdf
2026-02-19 I-485 Rejection.pdf
2026-03-01 I-485 NOID.pdf
2024-12-15 NVC Notice.pdf
2026-02-10 BIA Decision.pdf
```

### 4.2 Government Documents

**A. Criminal histories, FOIA responses, client-specific government records:**
Go in the client's `FOIAs/` subfolder.

```
[date] [Agency] Criminal History.pdf
[date] [Agency] FOIA Response.pdf
[date] [Agency] FOIA Confirmation.pdf
```

**B. Policy documents, bulletins, general government letters:**
Not client-specific — go in `_No Client/`.

```
[date] [Agency] [Document Type].pdf
```

**How to distinguish:** A document addressed to a specific client or referencing
a specific case number → client folder. Policy docs with no client reference →
`_No Client/`.

### 4.3 Court Documents

```
[date] [Document Type] - [Case Reference].pdf
```

Include the case reference because court documents without context are hard to
identify later.

**Identify the specific filing type — never use generic names like "Court
Filing."** Check in order:
1. Cover page / caption
2. Page headers or footers
3. Case caption block

**Conformed copies:** If a filing prepared by your firm bears a court filing
stamp ("FILED", "E-FILED", clerk's stamp), it is a conformed copy. Add
"CONFORMED" to the filename.

**How to tell if a filing is yours:** Your firm name appears in the top-right
corner or caption. Update this to your firm name:

```
[YOUR FIRM NAME]
```

**Examples:**
```
2026-02-12 Guardianship Petition.pdf
2026-03-01 Motion to Continue CONFORMED.pdf
2026-02-10 BIA Decision.pdf
1993-11-10 Court Sentencing.pdf
```

### 4.4 Client Correspondence

```
[date] [Letter Type] - [Subject].pdf
```

**Examples:**
```
2026-02-13 Client Letter - Immigration Hearing.pdf
2026-02-18 Client Letter - File Closed.pdf
2026-02-19 Third Party Letter - [Sender] ([Subject]).pdf
```

### 4.5 Client Files

```
[date] [Document Type].pdf
```

**Examples:**
```
2026-02-12 Client Intake.pdf
2026-02-12 Client Invoice.pdf
2026-02-12 Trust Account Check ($800).pdf
```

Dollar amounts on checks/invoices are useful to include.

### 4.6 IDs, Physical Documents & Cards

Physical documents — EAD cards, green cards, passports, state IDs, consular
cards — go directly in the client folder, not in `Receipt Notices/`.

```
[date] [Document Type].pdf
```

**Examples:**
```
2026-02-17 Passport.pdf
2026-02-17 State ID.pdf
2026-03-01 EAD Card.pdf
2026-03-01 Green Card.pdf
2026-02-17 Matricula Consular.pdf
```

### 4.7 Notes

**The handwritten content always controls identification.**

```
[date] Notes.pdf                   ← client identified
[date] Notes - [Subject].pdf      ← client identified, subject clear
[date] Notes (Unreadable).pdf     ← cannot identify client → _Unreadable
```

Use vision to attempt to read handwritten content. Look for:
- A client name at the top of the page
- Case references, docket numbers, form numbers
- Dates that help identify the file

If handwriting is illegible, file goes to `_Unreadable/`.

### 4.8 Closed File Contact Sheets

*Customize this section if your firm uses a standard closed file cover form.
If not, delete it.*

Your office uses a "CLOSED FILE / Pick-Up — CONTACT SHEET" form as a cover
sheet when scanning closed client files. It has a "Client:" field.

**Full closed file scan** (cover sheet + documents behind it):
Read the "Client:" field on page 1. File the entire scan into the client folder.
```
[date] Closed File.pdf
```

**Standalone contact sheet** (just the form, no file attached):
Goes in `_No Client/`.
```
[date] Closed File Contact Sheet.pdf
```

**How to distinguish:** Check page count. Standalone = 1–2 pages. Full file =
many pages.

### 4.9 Attorney Personal Documents

Documents belonging to the attorney personally, not a client. Go in `_No Client/`.

```
[date] [Descriptive Name].pdf
```

For foreign-language documents, keep the original title and add an English
descriptor if helpful.

### 4.10 Practice-Area Specific

*Add any document types specific to your practice areas here.*

Example for U-Visa practices:
```
[date] U-Visa Application.pdf     ← I-918 + supporting docs packet
```

---

## 5. Unreadable Documents

Always try vision before giving up on OCR:
1. Does OCR produce meaningful text? → Use it.
2. If not, extract page 1 as PNG and read visually.
3. Can you identify client and document type? → Sort it.
4. Can you identify document type but not client? → `_No Client/`.
5. Completely unreadable? → `_Unreadable/`.

```
[date] Notes (Unreadable).pdf     ← legible as notes, client unreadable
[date] Unreadable Scan.pdf        ← cannot determine what it is
```

---

## 6. Edge Cases

**Duplicate scans:** Add `(2)`, `(3)` suffixes. Both copies go to the same folder.

**Printed pages with handwritten annotations:** Handwriting controls. See §4.7.

**Multi-document scans:** Read the full file and identify the primary content.
File as a single unit. Do not split.

**Large files (> 50 MB):** PyMuPDF page-by-page OCR is slow (20–30 min).
This is expected.

**Unidentifiable files:** Send to `_Unreadable/` as `[date] Unreadable Scan.pdf`.
Never guess a client name — a wrong filing is worse than no filing.

**Filename collisions:** Add `(2)`, `(3)` suffixes. Never overwrite.

**OCR failure + vision failure:** Move to `_Unreadable/`, log `OCR_FAILED`.

---

## 7. Rename Safety Rules

1. Check for collisions before every move. Add numeric suffix, never overwrite.
2. Use `shutil.move()` for all file moves. Not `os.rename()`.
3. Create destination folders with `os.makedirs(path, exist_ok=True)`.
4. Log every move to `sort-scans.log`.

---

## 8. Changelog

| Date | Change |
|------|--------|
| [date] | Initial conventions for [YOUR FIRM NAME]. |
