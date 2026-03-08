import os
import json
from pdf_editor_agent import PDFDeSynthesizer, create_pdf_editor_agent
from pwc_renderer import render_report

def run_verification():
    print("--- [VERIFICATION] Regenerative PDF Synthesis Row-Trip ---")
    
    # 1. Ensure we have a sample PDF to start with
    source_pdf = "test_pwc_report.pdf"
    if not os.path.exists(source_pdf):
        print("Creating initial sample PDF...")
        # Use simple component feed to create a baseline
        baseline = {
            "ticker": "AAPL",
            "title": "Quarterly Update Analysis",
            "date": "March 2027",
            "components": [
                {
                    "type": "hero",
                    "title": "APPLE INC (FY2027)",
                    "subtitle": "Performance Review"
                },
                {
                    "type": "text",
                    "title": "EXECUTIVE SUMMARY",
                    "content": "Fiscal year 2027 was a breakout year for Apple."
                }
            ]
        }
        render_report(baseline, source_pdf)

    # 2. De-synthesize
    print("De-synthesizing PDF...")
    deserializer = PDFDeSynthesizer(source_pdf)
    report_json = deserializer.desynthesize()
    print(f"Original Date extracted: {report_json['date']}")

    # 3. Modify with Agent (Simulated)
    print("Modifying with Regenerative Agent...")
    # For verification, we manually apply a change to ensure deterministic testing
    # but we'll use the LLM to verify it can handle the prompt logic
    agent = create_pdf_editor_agent()
    # In a real scenario, we'd call the LLM here. Let's do it.
    from google.genai import Client
    client = Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")
    
    prompt = "change fiscal year to 2026 and respect the same format for the rest of the pdf"
    user_msg = f"Original Report JSON:\n{json.dumps(report_json, indent=2)}\n\nUSER MODIFICATION REQUEST: {prompt}"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_msg,
        config={"system_instruction": agent.instruction}
    )
    
    modified_json_str = response.text.strip()
    if modified_json_str.startswith("```json"):
        modified_json_str = modified_json_str.replace("```json", "").replace("```", "").strip()
    
    modified_json = json.loads(modified_json_str)
    print(f"Modified Date in JSON: {modified_json['date']}")

    # 4. Regenerate
    print("Regenerating PDF...")
    output_pdf = "verified_regenerative_report.pdf"
    render_report(modified_json, output_pdf)
    print(f"Regenerated PDF saved to {output_pdf}")

    # 5. Visual Check (Page 1)
    from verify_pdf_image import convert_pdf_to_png
    convert_pdf_to_png(output_pdf, "verified_regenerative_report_preview.png")
    print("Visual preview saved to verified_regenerative_report_preview.png")

if __name__ == "__main__":
    run_verification()
