import os
import time
import json
import asyncio
import traceback
from typing import AsyncGenerator
import fitz  # PyMuPDF
import vertexai
from vertexai.generative_models import GenerativeModel

# Ensure your GOOGLE_CLOUD_PROJECT / PROJECT_ID env vars are set properly
vertexai.init(project=os.environ.get("PROJECT_ID", "vtxdemos"), location=os.environ.get("LOCATION", "us-central1"))

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

async def run_regenerative_pipeline(pdf_path: str, prompt: str) -> AsyncGenerator[str, None]:
    """
    Executes the High-Fidelity Regenerative Pipeline.
    Instead of recreating the PDF from scratch, it uses LLMs to identify targeted text replacements,
    and then applies visual patches directly over the original PDF preserving 100% of formatting.
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
        # Stage 1: Snapshot De-synthesis (Decomposition)
        # ---------------------------------------------------------------------
        yield format_sse("Snapshot Analysis", "running")
        
        def _extract_pages():
            doc = fitz.open(pdf_path)
            pages = []
            for i in range(len(doc)):
                text = doc.load_page(i).get_text("text").strip()
                if text:
                    pages.append({"page_idx": i, "text": text})
            doc.close()
            return pages
            
        document_pages = await loop.run_in_executor(None, _extract_pages)
        yield format_sse("Snapshot Analysis", "completed", result_data={"pages_found": len(document_pages)})

        # ---------------------------------------------------------------------
        # Stage 2: Parallel Intelligence Routing (Targeted Patch Generation)
        # ---------------------------------------------------------------------
        yield format_sse("Parallel Intelligence Routing", "running")
        
        # User requested gemini-2.5-flash for parallelism
        model_25_flash = GenerativeModel("gemini-2.5-flash", system_instruction=(
            "You are a precise document updater. Read the provided page text and the user's directive. "
            "Identify what needs to be changed on this specific page based on the directive. "
            "Return a JSON array of objects representing text replacements: "
            "`[{\"find\": \"exact text from page to replace\", \"replace\": \"new text\"}]`. "
            "If no changes are needed on this page, return an empty array `[]`. "
            "CRITICAL: The `find` text MUST EXACTLY MATCH a contiguous substring from the provided page text. "
            "Do not hallucinate matches. Output STRICTLY VALID JSON."
        ))

        async def analyze_page(page_info):
            user_msg = f"User Directive: {prompt}\n\n--- Page {page_info['page_idx'] + 1} Text ---\n{page_info['text']}"
            def _run():
                res = model_25_flash.generate_content(user_msg, generation_config={"response_mime_type": "application/json"})
                patches = json.loads(_clean_json(res.text))
                for p in patches:
                    p["page_idx"] = page_info["page_idx"]
                return patches
            try:
                # Fast parallel execution
                return await loop.run_in_executor(None, _run)
            except Exception as e:
                print(f"Error on page {page_info['page_idx']}: {e}")
                return []

        all_patches = []
        # Run all pages concurrently
        results = await asyncio.gather(*(analyze_page(p) for p in document_pages))
        for res in results:
            if isinstance(res, list):
                all_patches.extend(res)

        yield format_sse("Parallel Intelligence Routing", "completed", result_data={"patches_proposed": len(all_patches)})

        # ---------------------------------------------------------------------
        # Stage 3: Aesthetic Evaluation Layer (Validation & Consolidation)
        # ---------------------------------------------------------------------
        yield format_sse("Aesthetic Evaluation Layer", "running")
        
        # User requested gemini-3-flash-preview for sequential/non-parallel logic
        model_3_flash = GenerativeModel("gemini-3-flash-preview", system_instruction=(
            "You are the Aesthetic Evaluator (Gatekeeper). Review the proposed text replacement patches against the original user prompt. "
            "Ensure the replacements are logical, factually consistent with the prompt, and don't introduce visual regressions (like overly long strings). "
            "Output the finalized, validated JSON array of patches `[{\"find\": \"...\", \"replace\": \"...\"}]`. "
            "If a patch is invalid or hallucinated, omit it. Do NOT change the JSON structure."
        ))

        async def run_evaluator():
            if not all_patches:
                return []
            user_msg = f"User Directive: {prompt}\n\nProposed Patches from Parallel Experts:\n{json.dumps(all_patches, indent=2)}\n\nValidate and return the final JSON array. Include the 'page_idx' field if it was provided."
            def _run():
                res = model_3_flash.generate_content(user_msg, generation_config={"response_mime_type": "application/json"})
                return json.loads(_clean_json(res.text))
            try:
                validated = await loop.run_in_executor(None, _run)
                return validated
            except Exception as e:
                print(f"Evaluation error: {e}")
                return all_patches # Fallback to unvalidated patches if 3.0 fails

        final_validated_patches = await run_evaluator()
        yield format_sse("Aesthetic Evaluation Layer", "completed", result_data={"patches_validated": len(final_validated_patches)})

        # ---------------------------------------------------------------------
        # Stage 4: Server-Side PDF Synthesis (High-Fidelity Patching)
        # ---------------------------------------------------------------------
        yield format_sse("Server-Side PDF Synthesis", "running")
        
        def _apply_in_place_patches():
            """Applies visual patches (whiteout + text overlay) onto the original PDF."""
            doc = fitz.open(pdf_path)
            output_path = pdf_path.replace(".pdf", "_regenerated.pdf")
            
            patched_regions = {}
            # Sort patches by length to replace longest strings first
            sorted_patches = sorted(final_validated_patches, key=lambda x: len(x.get("find", "")), reverse=True)
            
            for patch in sorted_patches:
                search_text = patch.get("find")
                replacement_text = patch.get("replace")
                if not search_text or not replacement_text or search_text == replacement_text:
                    continue
                
                # If page_idx is given, only search that page, else search all
                target_pages = [patch.get("page_idx")] if "page_idx" in patch else range(len(doc))
                
                for page_idx in target_pages:
                    if page_idx is None or page_idx >= len(doc):
                        continue
                    page = doc[page_idx]
                    if page_idx not in patched_regions:
                        patched_regions[page_idx] = []
                    
                    text_instances = page.search_for(search_text)
                    for inst in text_instances:
                        # Prevent overlapping patches
                        if any(inst.intersects(prev_rect) for prev_rect in patched_regions[page_idx]):
                            continue

                        # Extract original styling
                        dict_content = page.get_text("dict", clip=inst + (-2, -2, 2, 2))
                        font_size = 9
                        font_color = (0, 0, 0)
                        font_name = "helv"
                        origin = inst.bl + (0, -1)
                        
                        found_style = False
                        for block in dict_content.get("blocks", []):
                            if block.get("type") != 0: continue
                            for line in block.get("lines", []):
                                for span in line.get("spans", []):
                                    if search_text.lower() in span["text"].lower() or inst.intersects(span["bbox"]):
                                        font_size = span["size"]
                                        c = span["color"]
                                        font_color = (((c >> 16) & 0xFF) / 255.0, ((c >> 8) & 0xFF) / 255.0, (c & 0xFF) / 255.0)
                                        raw_font = span["font"].lower()
                                        font_name = "helv" if "sans" in raw_font or "inter" in raw_font else "tiro" if "serif" in raw_font else "helv"
                                        origin = fitz.Point(span["origin"])
                                        found_style = True
                                        break
                                if found_style: break
                            if found_style: break
                        
                        # Erase and overlay
                        # Expand mask slightly to cover anti-aliasing
                        mask_rect = inst + (-0.5, -0.5, 0.5, 0.5)
                        page.draw_rect(mask_rect, color=(1, 1, 1), fill=(1, 1, 1))
                        page.insert_text(origin, replacement_text, fontsize=font_size, color=font_color, fontname=font_name)
                        patched_regions[page_idx].append(inst)
            
            doc.save(output_path)
            doc.close()
            return output_path
            
        output_pdf_path = await loop.run_in_executor(None, _apply_in_place_patches)
        
        yield format_sse("Server-Side PDF Synthesis", "completed", result_data={"output_path": output_pdf_path, "modified_content": final_validated_patches})
        yield format_sse("Pipeline Complete", "success")

    except Exception as e:
        traceback.print_exc()
        yield format_sse("Pipeline Error", "failed", error=str(e))
