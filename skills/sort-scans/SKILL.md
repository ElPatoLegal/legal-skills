---
name: sort-scans
description: "OCR, identify, name, and file scanned legal documents. Reads each PDF using text extraction and vision, determines the client and document type, applies your firm's naming conventions, and moves files into the correct folders — silently, without prompting. Trigger on: 'sort scans', 'process scans', 'file the scans', 'sort the PDFs', 'process the inbox'."
practice_area: multi
jurisdiction: any
platform: windows
dependencies:
  - python >= 3.10
  - tesseract-ocr (system install)
  - ocrmypdf (pip)
  - pdfplumber (pip)
  - pymupdf (pip)
  - pillow (pip)
last_verified: 2026-05-14
freshness_window: 12 months
license: MIT
---

# Sort Scans

> **Target environment: Windows PowerShell via Claude Code CLI.**
> Do not run this skill in a Linux environment. If the OS is not Windows, stop
> and tell the user this skill is designed for Windows only.

This skill processes new scanned documents for a law firm. It OCRs files, reads
their contents, names them per your office convention, and files them into the
correct folder under `Sorted/`.

**Before making any naming or filing decisions, read the conventions file:**
`<skill_dir>/references/conventions.md`

That file is your authoritative source for all naming and filing rules. Copy it
from `conventions-template.md`, customize it for your firm, and save it as
`conventions.md` alongside it. This skill reads `conventions.md` at runtime.

---

## Prerequisites (first-time setup only)

Run these once. Do not check or reinstall on every run.

- **Python 3.10+**
- **Tesseract OCR** — `choco install tesseract` or download from
  https://github.com/UB-Mannheim/tesseract/wiki — must be on PATH
- **Python packages:** `pip install ocrmypdf pdfplumber pymupdf pillow`

---

## Setup

**Conventions file:** Copy `references/conventions-template.md` to
`references/conventions.md` and fill in your firm-specific details. The skill
will not run correctly without a populated conventions file.

**Staff names file:** Copy `references/staff-names-template.txt` to
`references/staff-names.txt` and replace the placeholder names with your actual
staff. One name per line. The skill uses this to avoid misidentifying staff
members as clients.

**Scans folder:** Determine the scans root at runtime. Look for a folder named
`Scans` in the current working directory, or check if the CWD itself is the
scans folder. The user may also pass the path as an argument. If the scans
folder cannot be found, stop with an error — do not prompt the user.

**This skill runs silently.** Do not prompt the user for approval or
confirmation at any step. Review your own plan internally and execute it.

**Error policy:** If any individual file fails, skip it, move it to
`_Unreadable/`, log the error, and continue. Never stop the entire run because
of one file.

---

## Logging

Maintain an append-only log at `<scans_root>/Sorted/sort-scans.log`.

```
[YYYY-MM-DD HH:MM:SS] <original filename> → <destination path> (<status>)
```

Status values: `OK`, `OCR_FAILED`, `UNREADABLE`, `SKIPPED`, `ERROR: <detail>`

Use blind append (`open(log_path, "a")`) — never read or parse the log.

---

## Workflow

### Step 1: Find unsorted files

List all PDF files in the scans root (not in any subfolder). Files already in
`Sorted/` or other subfolders are skipped.

```python
import os

scans_root = None
candidates = [
    os.path.join(os.getcwd(), "Scans"),
    os.getcwd(),
]
for candidate in candidates:
    if os.path.isdir(candidate):
        scans_root = candidate
        break

if scans_root is None:
    raise RuntimeError("Cannot find Scans folder. Pass the path as an argument.")

for subdir in ["Sorted", "Sorted/_No Client", "Sorted/_Unreadable"]:
    os.makedirs(os.path.join(scans_root, subdir), exist_ok=True)

unsorted = [
    f for f in os.listdir(scans_root)
    if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(scans_root, f))
]
```

Report how many files were found and their sizes before doing anything else.

### Step 2: OCR each file

Check for an existing text layer first:

```python
import pdfplumber
with pdfplumber.open(path) as pdf:
    text = " ".join(p.extract_text() or "" for p in pdf.pages[:3])
already_ocrd = len(text.strip()) > 50
```

Choose the OCR strategy by file size:

| File size | Strategy |
|-----------|----------|
| < 15 MB | `ocrmypdf --skip-text --rotate-pages --deskew --jobs 1` |
| 15–50 MB | `ocrmypdf` in 50-page chunks (`--pages N-M`) |
| > 50 MB | PyMuPDF + tesseract page-by-page |

**Standard ocrmypdf:**
```python
import shutil, tempfile, subprocess
with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
    tmp_path = tmp.name
result = subprocess.run(
    ["python", "-m", "ocrmypdf", "--skip-text", "--rotate-pages",
     "--deskew", "--jobs", "1", path, tmp_path],
    capture_output=True, text=True, timeout=300
)
if result.returncode == 0:
    shutil.move(tmp_path, path)
```

**Large file (> 50 MB) — PyMuPDF:**
```python
import fitz
doc = fitz.open(path)
for page in doc:
    if len(page.get_text().strip()) > 20:
        continue
    tp = page.get_textpage_ocr(dpi=150, language="eng", full=True)
    for x0, y0, x1, y1, word, *_ in tp.extractWORDS():
        fontsize = max(y1 - y0, 4)
        page.insert_text(fitz.Point(x0, y1), word + " ",
                         fontsize=fontsize, render_mode=3, color=(0,0,0))
with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
    tmp_path = tmp.name
doc.save(tmp_path, deflate=True, garbage=3)
doc.close()
shutil.move(tmp_path, path)
```

Use `render_mode=3` (invisible text) so the visual appearance is unchanged.

If OCR fails: move to `_Unreadable/`, log `OCR_FAILED`, continue.

### Step 3: Identify each file

Read the conventions file to understand what document types and naming patterns
apply. Then, for each file, determine:

- **Client name** (if any)
- **Document type**
- **Document date** — use the date on the document itself, not the scan date.
  See the conventions file for which date to use by document type.

For most files, the first 1–2 pages are enough. Use `pdfplumber` for text
extraction.

**Staff name check:** Read `references/staff-names.txt`. If a name from that
list appears prominently on a document (e.g., email inbox owner, addressee),
they are NOT the client. Keep looking — the client name is usually elsewhere:
handwritten annotation, email body, or referenced in the text.

**For handwritten or image-only files — use vision:**
```python
import fitz
doc = fitz.open(path)
pix = doc[0].get_pixmap(dpi=150)
pix.save("page1.png")
# Read the image with vision to identify the document
```

Do not rely solely on OCR for handwritten content. If OCR returns garbage,
always try visual recognition before giving up.

If a document is a printed page with handwritten notes on it, the handwriting
controls identification — not the printed content underneath.

### Step 4: Name and assign destinations

Apply all naming rules from `references/conventions.md`. Pay particular
attention to:

- The `USE_CLIENT_FOLDERS` flag (§2 of conventions) — controls whether files
  go into per-client folders or flat into `Sorted/` with the client name in
  the filename
- The date prefix rules (§3) — document date, not scan date
- The document-type naming patterns (§4)

### Step 5: Internal review

Before executing any moves, review the full plan internally:
- Does every filename follow conventions?
- Are destination folders correct?
- Are there filename collisions with existing files?

Fix any issues yourself. Do not prompt the user.

### Step 6: Execute moves

Create destination folders as needed (`os.makedirs(path, exist_ok=True)`).
Check for collisions before every move — add `(2)`, `(3)` suffixes, never
overwrite. Use `shutil.move()` for all moves. Log every move.

### Step 7: Report

After all moves complete, print a summary:
- Files processed
- Files OCR'd vs. already had text
- Files filed (and to which folder/client)
- Files in `_No Client/`
- Files in `_Unreadable/`
- Any errors needing manual attention

---

## Bundled scripts

Two standalone scripts are included in `scripts/`:

- **`ocr_files.py`** — batch OCR utility; can be run independently to OCR
  files without sorting them. Useful for pre-processing a large batch.
  Usage: `python ocr_files.py <scans_root> [file1.pdf ...]`

- **`extract_client_from_coversheet.py`** — detects closed file cover sheets
  and crops a tight band around the "Client:" field for vision reading. Saves
  ~90% of image tokens vs. sending the full page. Can be called directly or
  used as a reference for the cover sheet detection logic.
  Usage: `python extract_client_from_coversheet.py <pdf_path> <output.png>`
