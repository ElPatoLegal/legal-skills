"""Extract the Client name region from a Closed File cover sheet.

Usage: python extract_client_from_coversheet.py <pdf_path> <output_png>

Uses OCR text positions to locate the "Client:" label, then crops a tight band
around it and saves as a small PNG for vision-based reading. This avoids sending
the full page image to vision, saving ~90% of image tokens.

Returns exit code 0 if a cover sheet was detected, 1 otherwise.
Prints "COVERSHEET_DETECTED" or "NOT_A_COVERSHEET" to stdout.
"""

import sys
import os
import pdfplumber
import fitz
from PIL import Image
import tempfile


def is_coversheet(text):
    """Check if page text looks like a closed file cover sheet."""
    # Primary markers (printed text that OCRs reliably)
    strong = ["CONTACT SHEET"]
    # Supporting markers (any 2 of these reinforce the match)
    supporting = ["Client:", "lient:", "Closed Date", "File No", "Closed by",
                   "Pick-Up", "CLOSED FILE", "Action Log", "CL docs enclosed"]
    text_upper = text.upper()
    has_strong = any(m.upper() in text_upper for m in strong)
    support_count = sum(1 for m in supporting if m.upper() in text_upper)
    return has_strong or support_count >= 3


def find_client_y(words):
    """Find the Y position of the 'Client:' label in word list."""
    for w in words:
        if "lient" in w["text"]:
            return w["top"], w["bottom"]
    return None, None


def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_client_from_coversheet.py <pdf_path> <output_png>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_png = sys.argv[2]

    # Extract text and word positions from page 1
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text() or ""
        words = page.extract_words()
        page_height = page.height

    if not is_coversheet(text):
        print("NOT_A_COVERSHEET")
        sys.exit(1)

    print("COVERSHEET_DETECTED")

    # Find Client: label position
    client_top, client_bottom = find_client_y(words)

    if client_top is not None:
        # Crop around Client line: from slightly above to ~1.5 lines below
        line_height = client_bottom - client_top
        crop_top = max(0, client_top - line_height)
        crop_bottom = min(page_height, client_bottom + line_height * 2)
        top_pct = crop_top / page_height
        bot_pct = crop_bottom / page_height
    else:
        # Fallback: use fixed region where Client typically appears (18-26%)
        top_pct = 0.17
        bot_pct = 0.26

    # Render page and crop
    doc = fitz.open(pdf_path)
    pix = doc[0].get_pixmap(dpi=150)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp_path = tmp.name
    tmp.close()
    pix.save(tmp_path)
    doc.close()

    img = Image.open(tmp_path)
    w, h = img.size
    cropped = img.crop((0, int(h * top_pct), w, int(h * bot_pct)))
    cropped.save(output_png)
    img.close()

    os.unlink(tmp_path)
    print(f"CROP_SAVED: {output_png} ({cropped.size[0]}x{cropped.size[1]})")


if __name__ == "__main__":
    main()
