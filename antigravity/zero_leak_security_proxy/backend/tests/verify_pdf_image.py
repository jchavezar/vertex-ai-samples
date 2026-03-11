import fitz # PyMuPDF
import os

def convert_pdf_to_png(pdf_path, img_path):
    if os.path.exists(pdf_path):
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        pix.save(img_path)
        print(f"Saved {img_path}")
        return True
    else:
        print(f"Error: {pdf_path} not found")
        return False

if __name__ == "__main__":
    convert_pdf_to_png("test_pwc_report.pdf", "test_pwc_report_page1.png")
