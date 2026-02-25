import os
import io
import base64
import fitz
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any
from pypdf import PdfReader, PdfWriter

def split_pdf_logically(pdf_bytes: bytes, max_pages_per_chunk: int = 1) -> List[Dict[str, Any]]:
    """
    Splits a PDF locally into separate single-page chunks to be parsed independently.
    Uses in-memory bytes streams to optimize latency instead of disk writes.
    Returns a list of dicts containing the bytes and metadata.
    """
    chunks = []
    
    # Read the PDF from memory
    pdf_stream = io.BytesIO(pdf_bytes)
    reader = PdfReader(pdf_stream)
    num_pages = len(reader.pages)

    for i in range(0, num_pages, max_pages_per_chunk):
        writer = PdfWriter()
        end_idx = min(i + max_pages_per_chunk, num_pages)
        for j in range(i, end_idx):
             writer.add_page(reader.pages[j])
        
        # Write the split page(s) to a memory buffer
        out_stream = io.BytesIO()
        writer.write(out_stream)
        chunk_bytes = out_stream.getvalue()
        out_stream.close()
        
        chunks.append({
             "start_page": i + 1,
             "end_page": end_idx,
             "pdf_bytes": chunk_bytes,
             "mime_type": "application/pdf"
        })

    pdf_stream.close()
    return chunks

def pdf_page_to_image(pdf_bytes: bytes, page_num: int) -> bytes:
    """Converts a specific PDF page (0-indexed) to a JPEG image bytes."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if page_num >= len(doc):
        return b""
    page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Higher resolution
    img_data = pix.tobytes("jpeg")
    return img_data

def draw_bounding_boxes(image_bytes: bytes, entities_with_boxes: List[Any], original_page_num: int) -> bytes:
    """
    Draws bounding boxes over the image and adds a sidebar legend.
    entities_with_boxes should be a list of ExtractedEntity objects with bounding_box mapped.
    """
    if not image_bytes or not entities_with_boxes:
        return image_bytes
        
    im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = im.size
    draw = ImageDraw.Draw(im)
    
    # Modern high-contrast vibrant palette
    VIBRANT_COLORS = [
        "#FF3D00", "#00E676", "#2979FF", "#FFEA00", "#D500F9", 
        "#00E5FF", "#FF9100", "#1DE9B6", "#C6FF00", "#FF1744"
    ]
    
    try:
        base_size = max(20, int(min(width, height) / 35))
        label_font = ImageFont.truetype("Arial.ttf", size=base_size)
    except OSError:
        label_font = ImageFont.load_default()

    # Draw boxes
    for i, entity in enumerate(entities_with_boxes):
        if not hasattr(entity, 'box_2d') or not entity.box_2d or len(entity.box_2d) != 4:
            continue
            
        bb = entity.box_2d
        y_min, x_min, y_max, x_max = [int(v / 1000 * (height if j%2==0 else width)) 
                                      for j, v in enumerate(bb)]
        
        color = VIBRANT_COLORS[i % len(VIBRANT_COLORS)]
        
        # Bounding box
        draw.rectangle(((x_min, y_min), (x_max, y_max)), outline=color, width=4)
        draw.rectangle(((x_min-1, y_min-1), (x_max+1, y_max+1)), outline="white", width=1)
        
        # Pill Tag
        tag_text = f" {i+1} "
        try:
            tw, th = label_font.getbbox(tag_text)[2:]
        except:
            tw, th = 30, 30

        pill_padding = 6
        pill_rect = [x_min, y_min - th - (pill_padding * 2), x_min + tw + (pill_padding * 2), y_min]
        if pill_rect[1] < 0:
            pill_rect[1] = y_min
            pill_rect[3] = y_min + th + (pill_padding * 2)

        draw.rectangle(pill_rect, fill=color)
        draw.text((pill_rect[0] + pill_padding, pill_rect[1] + pill_padding), tag_text, fill="white", font=label_font)

    # 3. Create Sidebar
    sidebar_width = 500
    new_width = width + sidebar_width
    combined = Image.new("RGB", (new_width, height), (15, 15, 20)) # Deep navy-black
    combined.paste(im, (0, 0))
    
    s_draw = ImageDraw.Draw(combined)
    title_size = max(28, int(height / 30))
    body_size = max(22, int(height / 40))
    
    try:
        title_font = ImageFont.truetype("Arial.ttf", size=title_size)
        body_font = ImageFont.truetype("Arial.ttf", size=body_size)
    except OSError:
        title_font = body_font = ImageFont.load_default()

    s_draw.text((width + 30, 30), f"PAGE {original_page_num} ENTITIES", fill="#64B5F6", font=title_font)
    s_draw.line((width + 30, 30 + title_size + 10, width + 470, 30 + title_size + 10), fill="#2C2C3E", width=2)

    current_y = 60 + title_size * 2
    for i, entity in enumerate(entities_with_boxes):
        if not hasattr(entity, 'box_2d') or not entity.box_2d or len(entity.box_2d) != 4:
            continue
            
        color = VIBRANT_COLORS[i % len(VIBRANT_COLORS)]
        label_text = f"[{entity.entity_type}] {entity.content_description[:30]}..."
        
        # Badge
        badge_w, badge_h = 45, 45
        s_draw.rounded_rectangle([width + 30, current_y, width + 30 + badge_w, current_y + badge_h], radius=8, fill=color)
        s_draw.text((width + 42, current_y + 8), str(i+1), fill="white", font=body_font)
        
        # Text
        s_draw.text((width + 90, current_y + 8), label_text, fill="#E0E0E0", font=body_font)
        
        current_y += int(badge_h * 1.6)

    output = io.BytesIO()
    combined.save(output, format="JPEG", quality=85)
    return output.getvalue()
