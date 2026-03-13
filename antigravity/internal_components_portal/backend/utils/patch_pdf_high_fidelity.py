
import fitz  # PyMuPDF
import os

def patch_pdf(input_path, output_path, search_text, replacement_text):
    print(f"Opening PDF: {input_path}")
    doc = fitz.open(input_path)
    
    found = False
    for page in doc:
        # 1. Find the instances of search_text
        text_instances = page.search_for(search_text)
        
        for inst in text_instances:
            found = True
            print(f"Found '{search_text}' at {inst}. Patching...")
            
            # 2. Add a white rectangle to "erase" the old text
            # We add a small padding to ensure complete coverage
            rect = inst + (-1, -1, 1, 1)
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
            
            # 3. Add the replacement text in the same spot
            # We use a standard font for the prototype, but we could try to match
            page.insert_text(inst.bl + (0, -2), replacement_text, fontsize=10, color=(0, 0, 0))

    if found:
        doc.save(output_path)
        print(f"Successfully patched. Saved to: {output_path}")
    else:
        print(f"Text '{search_text}' not found in PDF.")
    
    doc.close()

if __name__ == "__main__":
    input_pdf = "/usr/local/google/home/jesusarguelles/IdeaProjects/vertex-ai-samples/antigravity/zero_leak_security_proxy/docs/08_HR_Compensation_Analysis_FY2024.pdf"
    output_pdf = "/tmp/patched_doc.pdf"
    
    # Text from the previous Gemini run that definitely exists
    target = "Engineering management equity is 15% below market"
    new_text = "Engineering management equity is now ALIGNED with the market."
    
    patch_pdf(input_pdf, output_pdf, target, new_text)
