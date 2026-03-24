from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 15)
        self.cell(0, 10, "CONFIDENTIAL - TRANSFER PRICING MASTER FILE", border=0, ln=1, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")

pdf = PDF()
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_font("Helvetica", size=12)

content = """
Transfer Pricing Agreement
Subject: Intercompany Royalty and Service Licensing
Region: Latin America (LATAM)
Date: October 1st, 2024

1. Purpose and Scope
This agreement outlines the terms and conditions regarding the intercompany transfer 
of intangible assets and the provision of technical services from the Global HQ to 
its subsidiary located in Brazil (LATAM Operations).

2. Royalty Rates and Markup
The parties agree to a royalty rate of 4.5% on net sales for the use of proprietary 
technology. For technical services rendered, cost plus a 5% markup will be applied. 
Notice: This markup may fall below the 8% local safe harbor requirement newly instituted 
by the Brazil Tax Authority for FY25.

3. OECD Guidelines Consistency
This agreement intends to align with the Arm's Length Principle as defined by the 
OECD Transfer Pricing Guidelines. Based on the functional analysis, the inter-quartile 
range for similar uncontrolled transactions falls between 3.2% and 5.8%.

4. Dispute Resolution
Any discrepancies or required addendums resulting from unilateral changes in local 
tax legislation shall be resolved through the generation of a Section 4 Addendum.

[End of Document]
"""

for line in content.strip().split('\n'):
    pdf.multi_cell(0, 10, txt=line)

pdf.output("../public/LATAM_Agreement_V4.pdf")
