import os
import json
import fitz  # PyMuPDF
from typing import List, Dict, Any
from google.adk.agents import Agent, LlmAgent
from google.adk.planners import BuiltInPlanner

# Direct import for local testing if needed
# from .internal_renderer import render_report

class PDFDeSynthesizer:
    """
    Converts a professional PDF back into a structured Component Feed.
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        self.doc = fitz.open(pdf_path)

    def desynthesize(self) -> Dict[str, Any]:
        """
        Simplified: Extract text groups to form components
        """
        report_data = {
            "ticker": "UNKNOWN",
            "title": "Investment Report",
            "date": "March 2026",
            "components": []
        }
        
        # Heuristic: First page first few lines are usually header
        page1 = self.doc.load_page(0)
        text_blocks = page1.get_text("blocks")
        
        # Sort blocks by y-coordinate then x-coordinate
        text_blocks.sort(key=lambda b: (b[1], b[0]))
        
        for block in text_blocks:
            text = block[4].strip()
            if not text:
                continue
            
            # Identify ticker (usually single word, uppercase, top right)
            if block[1] < 100 and block[0] > 400 and len(text.split()) == 1 and text.isupper():
                report_data["ticker"] = text
                continue
            
            # Identify Title
            if block[1] < 150 and ("Update" in text or "Analysis" in text):
                report_data["title"] = text
                continue
                
            # Identify Date
            if "202" in text and len(text.split()) <= 3 and block[1] < 200:
                report_data["date"] = text
                continue
            
            # Identify Section Titles (centered or bold or all caps)
            if text.isupper() and len(text.split()) < 10:
                report_data["components"].append({
                    "type": "text",
                    "title": text,
                    "content": ""
                })
            else:
                # Add content to last text component or create new
                if not report_data["components"]:
                    report_data["components"].append({
                        "type": "text",
                        "title": "General",
                        "content": text
                    })
                else:
                    last_comp = report_data["components"][-1]
                    if last_comp["type"] == "text":
                        if last_comp["content"]:
                            last_comp["content"] += "\n\n" + text
                        else:
                            last_comp["content"] = text
                    else:
                        report_data["components"].append({
                            "type": "text",
                            "title": "",
                            "content": text
                        })
                        
        return report_data

def create_pdf_editor_agent():
    """
    Creates an ADK agent that can modify PDF 'Component Feeds'.
    """
    
    modification_agent = LlmAgent(
        name="pdf_modification_agent",
        model="gemini-2.5-flash",
        description="I am an expert at modifying financial report structures.",
        instruction="""
        You will receive a Report Component Feed (JSON).
        User will ask for changes (e.g., 'Change fiscal year to 2026').
        Your job is to update the JSON structure while maintaining all other formatting.
        Ensure consistency: if a year changes, update it in headers, text, and tables.
        Output ONLY the final updated JSON.
        """
    )
    
    return modification_agent

if __name__ == "__main__":
    # Test on the generated report
    pdf_to_test = "test_internal_report.pdf"
    if os.path.exists(pdf_to_test):
        deserializer = PDFDeSynthesizer(pdf_to_test)
        report_json = deserializer.desynthesize()
        print(json.dumps(report_json, indent=2))
    else:
        print(f"Error: {pdf_to_test} not found. Run internal_renderer.py first.")
