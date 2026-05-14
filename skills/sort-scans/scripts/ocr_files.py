"""OCR scanned PDFs in the scans root folder.

Usage: python ocr_files.py <scans_root> [file1.pdf file2.pdf ...]
  If no files specified, OCRs all PDFs in scans_root that lack text layers.
"""

import sys, os, subprocess, tempfile, shutil, pdfplumber

os.environ["PATH"] = (
    os.environ.get("PATH", "")
    + os.pathsep
    + r"C:\Program Files\Tesseract-OCR"
)

SKIP_TEXT = "--skip-text"
ROTATE = "--rotate-pages"
DESKEW = "--deskew"
JOBS = "--jobs"


def has_text(path, min_chars=50):
    with pdfplumber.open(path) as pdf:
        text = " ".join(p.extract_text() or "" for p in pdf.pages[:3])
    return len(text.strip()) > min_chars


def ocr_small(path):
    """Standard ocrmypdf for files < 15 MB."""
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp_path = tmp.name
    tmp.close()
    try:
        result = subprocess.run(
            ["python", "-m", "ocrmypdf", SKIP_TEXT, ROTATE, DESKEW, JOBS, "1", path, tmp_path],
            capture_output=True, text=True, timeout=300,
            env=os.environ,
        )
        if result.returncode == 0:
            shutil.move(tmp_path, path)
            return True
        else:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return False
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        return False


def ocr_large(path):
    """PyMuPDF page-by-page OCR for files > 50 MB."""
    import fitz
    doc = fitz.open(path)
    for page in doc:
        if len(page.get_text().strip()) > 20:
            continue
        tp = page.get_textpage_ocr(dpi=150, language="eng", full=True)
        for x0, y0, x1, y1, word, *_ in tp.extractWORDS():
            fontsize = max(y1 - y0, 4)
            page.insert_text(
                fitz.Point(x0, y1), word + " ",
                fontsize=fontsize, render_mode=3, color=(0, 0, 0),
            )
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp_path = tmp.name
    tmp.close()
    doc.save(tmp_path, deflate=True, garbage=3)
    doc.close()
    shutil.move(tmp_path, path)
    return True


def ocr_chunked(path, pages_per_chunk=50):
    """ocrmypdf in chunks for files 15-50 MB."""
    with pdfplumber.open(path) as pdf:
        total = len(pdf.pages)
    for start in range(1, total + 1, pages_per_chunk):
        end = min(start + pages_per_chunk - 1, total)
        page_range = f"{start}-{end}"
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp_path = tmp.name
        tmp.close()
        try:
            result = subprocess.run(
                ["python", "-m", "ocrmypdf", SKIP_TEXT, ROTATE, DESKEW, JOBS, "1",
                 "--pages", page_range, path, tmp_path],
                capture_output=True, text=True, timeout=600,
                env=os.environ,
            )
            if result.returncode == 0:
                shutil.move(tmp_path, path)
            else:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                return False
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return False
    return True


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if len(sys.argv) < 2:
        print("Usage: python ocr_files.py <scans_root> [file1.pdf ...]")
        sys.exit(1)

    scans_root = sys.argv[1]
    if len(sys.argv) > 2:
        files = sys.argv[2:]
    else:
        files = [
            f for f in os.listdir(scans_root)
            if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(scans_root, f))
        ]

    for f in files:
        path = os.path.join(scans_root, f)
        size_mb = os.path.getsize(path) / (1024 * 1024)

        if has_text(path):
            print(f"SKIP: {f} (already has text)")
            continue

        if size_mb > 50:
            ok = ocr_large(path)
        elif size_mb > 15:
            ok = ocr_chunked(path)
        else:
            ok = ocr_small(path)

        print(f"{'OK' if ok else 'FAIL'}: {f} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
