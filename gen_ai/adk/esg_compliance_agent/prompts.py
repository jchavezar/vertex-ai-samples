GENERATE_ESG_TABLE = """
Role: Generate simple synthetic data for a Deloitte ESG audit demo.
Task: Create a single JSON array representing a "Tech Sustainability Compliance Tracker" table.
Provide 20 rows of data following this exact schema:
Record_ID (String, e.g., "REC-101")
Purchase_Date (Date, YYYY-MM-DD, last 12 months)
Tech_Item_Description (String, e.g., "500x Dell Laptops", "Nvidia H100 Clusters", "AWS Cloud Contract")
Estimated_CO2_Impact_Tons (Number, realistic estimate based on the item)
Required_Green_Action (String, e.g., "Plant 500 Trees", "Buy 100 Carbon Credits")
Compliance_Status (String, must be "Compliant" or "Pending Action")
Audit_Proof_Doc (String, filename e.g., "Cert-Trees-99.pdf". Can be null if Pending.)
Data Generation Rules (Crucial for the Demo):
Generate 19 "Compliant" Rows: These represent historical successes. They must have Compliance_Status: "Compliant" and a filename in Audit_Proof_Doc.
Generate exactly 1 "Target" Row: This is for the live demo.
Tech_Item_Description: "Bulk Purchase: 200x Dell Latitude 7440 for Field Audit"
Purchase_Date: Make it last week.
Compliance_Status: "Pending Action"
Audit_Proof_Doc: null (My agents will fill this in).
Output: Provide only the JSON array.
"""