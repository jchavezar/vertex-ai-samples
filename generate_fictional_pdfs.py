import os

def create_fictional_pdf(path, filename="fictional_sample.pdf"):
    content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Length 50 >>\nstream\n"
        b"BT /F1 12 Tf 100 700 Td (Fictional Document for Testing Purposes Only) Tj ET\n"
        b"endstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000213 00000 n \n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n314\n%%EOF\n"
    )
    full_path = os.path.join(path, filename)
    os.makedirs(path, exist_ok=True)
    with open(full_path, "wb") as f:
        f.write(content)
    print(f"Created fictional PDF at: {full_path}")

# Target directories
dirs = [
    "antigravity/multimodal_document_chat/docs",
    "antigravity/multimodal_document_chat/backend",
    "antigravity/multimodal_document_chat/frontend/public",
    "antigravity/llm_security_proxy_sharepoint/docs",
    "antigravity/stock-terminal-next/backend"
]

for d in dirs:
    create_fictional_pdf(d, "sample_fictional.pdf")
