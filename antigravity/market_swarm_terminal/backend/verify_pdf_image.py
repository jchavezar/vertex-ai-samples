import fitz # PyMuPDF
import os

pdf_path = "test_pwc_report.pdf"
img_path = "test_pwc_report_page1.png"

if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=150)
    pix.save(img_path)
    print(f"Saved {img_path}")
else:
    print(f"Error: {pdf_path} not found")
