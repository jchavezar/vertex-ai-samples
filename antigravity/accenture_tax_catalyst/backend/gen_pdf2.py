from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, height - 50, "CONFIDENTIAL - TRANSFER PRICING MASTER FILE")
    
    # Body text
    text_lines = [
        "Transfer Pricing Agreement",
        "Subject: Intercompany Royalty and Service Licensing",
        "Region: Latin America (LATAM)",
        "Date: October 1st, 2024",
        "",
        "1. Purpose and Scope",
        "This agreement outlines the terms and conditions regarding the intercompany transfer",
        "of intangible assets and the provision of technical services from the Global HQ to",
        "its subsidiary located in Brazil (LATAM Operations).",
        "",
        "2. Royalty Rates and Markup",
        "The parties agree to a royalty rate of 4.5% on net sales for the use of proprietary",
        "technology. For technical services rendered, cost plus a 5% markup will be applied.",
        "Notice: This markup may fall below the 8% local safe harbor requirement newly instituted",
        "by the Brazil Tax Authority for FY25.",
        "",
        "3. OECD Guidelines Consistency",
        "This agreement intends to align with the Arm's Length Principle as defined by the",
        "OECD Transfer Pricing Guidelines. Based on the functional analysis, the inter-quartile",
        "range for similar uncontrolled transactions falls between 3.2% and 5.8%.",
        "",
        "4. Dispute Resolution",
        "Any discrepancies or required addendums resulting from unilateral changes in local",
        "tax legislation shall be resolved through the generation of a Section 4 Addendum.",
        "",
        "[End of Document]"
    ]
    
    c.setFont("Helvetica", 12)
    y = height - 100
    for line in text_lines:
        c.drawString(50, y, line)
        y -= 20
        
    c.save()

if __name__ == "__main__":
    create_pdf("../public/LATAM_Agreement_V4.pdf")
