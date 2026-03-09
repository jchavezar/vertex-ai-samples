import os
import time
import json
import asyncio
import traceback
import io
import base64
from typing import AsyncGenerator

import fitz  # PyMuPDF
import matplotlib.pyplot as plt
import markdown
from markitdown import MarkItDown
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader

import vertexai
from vertexai.generative_models import GenerativeModel

# Ensure your GOOGLE_CLOUD_PROJECT / PROJECT_ID env vars are set properly
vertexai.init(project=os.environ.get("PROJECT_ID", "vtxdemos"), location="global")

def _clean_json(json_str: str) -> str:
    """Helper to strip markdown blocks from LLM JSON responses."""
    json_str = json_str.strip()
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    return json_str.strip()

# Initialize Agents
router_model = GenerativeModel("gemini-3.1-flash-lite-preview", system_instruction=(
    "You are the Architectural Router for document generation. You read an original document and a user directive. "
    "Your job is to plan the final document structure by breaking it down into a JSON array of blocks. "
    "Each block has a 'type' ('text', 'table', 'chart'). "
    "If a block is unchanged from the original, set 'needs_generation': false and provide its exact 'content' in markdown. "
    "If a block needs to be created or modified based on the directive, set 'needs_generation': true and provide an 'instruction' for the subagent. "
    "Output MUST be valid JSON: [{'type': 'text|table|chart', 'needs_generation': bool, 'content': '...', 'instruction': '...'}]."
))

text_agent = GenerativeModel("gemini-3.1-flash-lite-preview", system_instruction=(
    "You are the Text Agent. You write fluid, highly professional corporate narrative text. "
    "Given an instruction, generate the appropriate markdown text. Output raw markdown. Do not wrap in ```markdown."
))

table_agent = GenerativeModel("gemini-3.1-flash-lite-preview", system_instruction=(
    "You are the Table Agent. You format raw data into pristine, semantic markdown tables. "
    "Given an instruction and context, output the exact markdown table. Output raw markdown table only."
))

chart_agent = GenerativeModel("gemini-3.1-flash-lite-preview", system_instruction=(
    "You are the Chart Agent. You extract numerical data destined for charts. "
    "Given an instruction, return a JSON object with 'chart_type' ('bar', 'pie', 'line'), 'title', 'labels' (array of strings), and 'values' (array of numbers). "
    "CRITICAL: The length of the 'labels' array MUST EXACTLY MATCH the length of the 'values' array. "
    "If the table has multiple columns of values, select only ONE column to plot (or derive a single value per label) to ensure array lengths match. "
    "Output STRICTLY valid JSON."
))

async def run_regenerative_pipeline(pdf_path: str, prompt: str) -> AsyncGenerator[str, None]:
    """
    Executes the Modular Intelligence Routing Pipeline to construct flawless PDFs.
    """
    start_time_total = time.time()

    def format_sse(stage: str, status: str, result_data: dict = None, error: str = None) -> str:
        elapsed_ms = int((time.time() - start_time_total) * 1000)
        payload = {"stage": stage, "status": status, "elapsed_ms": elapsed_ms}
        if result_data:
            payload["result"] = result_data
        if error:
            payload["error"] = error
        return f"data: {json.dumps(payload)}\n\n"

    try:
        loop = asyncio.get_event_loop()

        # ---------------------------------------------------------------------
        # Stage 1: Document Extraction (MarkItDown)
        # ---------------------------------------------------------------------
        yield format_sse("Snapshot Analysis", "running")
        
        def _extract_markdown():
            md = MarkItDown()
            result = md.convert(pdf_path)
            return result.text_content
            
        original_markdown = await loop.run_in_executor(None, _extract_markdown)
        yield format_sse("Snapshot Analysis", "completed", result_data={"bytes_extracted": len(original_markdown)})


        # ---------------------------------------------------------------------
        # Stage 2: Parallel Intelligence Routing (Document Decomposition)
        # ---------------------------------------------------------------------
        yield format_sse("Parallel Intelligence Routing", "running")
        
        router_prompt = f"User Directive: {prompt}\n\n--- Original Document ---\n{original_markdown}"
        
        def _route():
            res = router_model.generate_content(router_prompt, generation_config={"response_mime_type": "application/json"})
            try:
                parsed = json.loads(_clean_json(res.text))
            except Exception as e:
                print(f"Error parsing router JSON: {e}")
                parsed = []
                
            blocks_out = []
            if isinstance(parsed, dict):
                # In case the model wrapped it in an object {"blocks": [...]}
                for k, v in parsed.items():
                    if isinstance(v, list):
                        blocks_out.extend(v)
            elif isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict):
                        blocks_out.append(item)
                    elif isinstance(item, list): # List of lists generated sometimes
                        blocks_out.extend([x for x in item if isinstance(x, dict)])
            return blocks_out
            
        blocks = await loop.run_in_executor(None, _route)
        yield format_sse("Parallel Intelligence Routing", "completed", result_data={"blocks_planned": len(blocks)})

        # ---------------------------------------------------------------------
        # Stage 3: Parallel Subagents Execution
        # ---------------------------------------------------------------------
        yield format_sse("Parallel Subagent Synthesis", "running")

        async def _process_block(block):
            if not block.get("needs_generation"):
                # Fast path markdown conversion
                html_content = markdown.markdown(block.get("content", ""), extensions=['tables'])
                return html_content

            instruction = block.get("instruction", "")
            b_type = block.get("type")

            if b_type == "text":
                res = await loop.run_in_executor(None, lambda: text_agent.generate_content(instruction).text)
                return markdown.markdown(res, extensions=['tables'])
                
            elif b_type == "table":
                res = await loop.run_in_executor(None, lambda: table_agent.generate_content(f"Data Context: {original_markdown}\n\nInstruction: {instruction}").text)
                return markdown.markdown(res, extensions=['tables'])

            elif b_type == "chart":
                def _gen_chart():
                    res = chart_agent.generate_content(f"Data Context: {original_markdown}\n\nInstruction: {instruction}", generation_config={"response_mime_type": "application/json"})
                    chart_spec = json.loads(_clean_json(res.text))
                    
                    labels = chart_spec.get("labels", [])
                    values = chart_spec.get("values", [])
                    c_type = chart_spec.get("chart_type", "bar")
                    title = chart_spec.get("title", "Chart")
                    
                    if not labels or not values:
                        return "<p><i>Chart data unavailable</i></p>"

                    # Enforce shape match to prevent matplotlib crashes
                    min_len = min(len(labels), len(values))
                    labels = labels[:min_len]
                    values = values[:min_len]

                    plt.figure(figsize=(8, 5))
                    if c_type == "pie":
                        plt.pie(values, labels=labels, autopct='%1.1f%%', colors=['#d04a02', '#2d5573', '#eb8c00', '#e0301e'])
                    elif c_type == "line":
                        plt.plot(labels, values, marker='o', color="#d04a02", linewidth=2)
                        plt.grid(True, linestyle="--", alpha=0.6)
                        plt.xticks(rotation=45, ha="right")
                    else: # bar
                        plt.bar(labels, values, color="#d04a02")
                        plt.grid(axis='y', linestyle="--", alpha=0.6)
                        plt.xticks(rotation=45, ha="right")
                        
                    plt.title(title, fontsize=14, color="#2d5573", fontweight="bold")
                    plt.tight_layout()
                    
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
                    plt.close()
                    buf.seek(0)
                    
                    encoded = base64.b64encode(buf.read()).decode('utf-8')
                    return f'<div class="chart-container"><img src="data:image/png;base64,{encoded}" alt="{title}"><div class="chart-caption">{title}</div></div>'
                
                return await loop.run_in_executor(None, _gen_chart)

            return ""

        # Run all subagents concurrently
        block_results = await asyncio.gather(*(_process_block(b) for b in blocks))
        
        final_html_content = "\n".join(block_results)
        
        yield format_sse("Parallel Subagent Synthesis", "completed", result_data={"agents_executed": sum(1 for b in blocks if b.get('needs_generation'))})

        # ---------------------------------------------------------------------
        # Stage 4: Server-Side PDF Synthesis (WeasyPrint)
        # ---------------------------------------------------------------------
        yield format_sse("Aesthetic Evaluation Layer", "running") # We map Aesthetic Evaluation to the compilation step
        
        def _compile_pdf():
            template_dir = os.path.join(os.path.dirname(__file__), "templates")
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template("report_skeleton.html")
            
            # Extract a sensible title
            doc_title = "Financial Audit Report"
            if blocks and blocks[0].get("content"):
                first_lines = blocks[0]["content"].split("\n")
                if first_lines and first_lines[0].startswith("#"):
                    doc_title = first_lines[0].replace("#", "").strip()

            rendered_html = template.render(
                document_title=doc_title,
                body_content=final_html_content
            )
            
            output_path = pdf_path.replace(".pdf", "_regenerated.pdf")
            
            # Write to disk to debug if necessary
            # with open(pdf_path.replace(".pdf", "_regenerated.html"), "w") as f:
            #     f.write(rendered_html)
                
            css_path = os.path.join(template_dir, "report_style.css")
            HTML(string=rendered_html, base_url=template_dir).write_pdf(output_path, stylesheets=[CSS(filename=css_path)])
            return output_path
            
        final_pdf_path = await loop.run_in_executor(None, _compile_pdf)

        yield format_sse("Aesthetic Evaluation Layer", "completed", result_data={"pdf_generated": True})
        
        # We replace the final stage name to match the UI expectations if needed, but the UI expects Server-Side PDF Synthesis
        yield format_sse("Server-Side PDF Synthesis", "completed", result_data={"output_path": final_pdf_path})
        yield format_sse("Pipeline Complete", "success")

    except Exception as e:
        traceback.print_exc()
        yield format_sse("Pipeline Error", "failed", error=str(e))

