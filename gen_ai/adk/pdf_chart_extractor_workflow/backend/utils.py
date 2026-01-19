import os
import io
import fitz  # PyMuPDF
from PIL import Image, ImageColor, ImageDraw, ImageFont
from typing import List, Dict, Any
from google.cloud import bigquery
from google.cloud import storage

def pdf_to_images(pdf_bytes: bytes) -> List[bytes]:
    """Converts PDF bytes to a list of JPEG image bytes."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Higher res
        img_data = pix.tobytes("jpeg")
        images.append(img_data)
    return images

def draw_legend_sidebar(image_bytes: bytes, boxes: List[Dict[str, Any]]) -> bytes:
    """
    Draws modern bounding boxes with colored 'pill' labels and a styled legend.
    """
    im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = im.size
    draw = ImageDraw.Draw(im)
    
    # Modern high-contrast vibrant palette
    VIBRANT_COLORS = [
        "#FF3D00", "#00E676", "#2979FF", "#FFEA00", "#D500F9", 
        "#00E5FF", "#FF9100", "#1DE9B6", "#C6FF00", "#FF1744"
    ]
    
    try:
        # Load a variable font size based on image scale
        base_size = max(20, int(min(width, height) / 35))
        label_font = ImageFont.truetype("Arial.ttf", size=base_size)
    except OSError:
        label_font = ImageFont.load_default()

    for i, bbox in enumerate(boxes):
        box = bbox.get("box_2d") or [bbox.get("ymin"), bbox.get("xmin"), bbox.get("ymax"), bbox.get("xmax")]
        
        y_min, x_min, y_max, x_max = [int(v / 1000 * (height if j%2==0 else width)) for j, v in enumerate(box)]
        
        color = VIBRANT_COLORS[i % len(VIBRANT_COLORS)]
        
        # 1. Draw smooth bounding box with inner & outer stroke for contrast
        draw.rectangle(((x_min, y_min), (x_max, y_max)), outline=color, width=6)
        draw.rectangle(((x_min-1, y_min-1), (x_max+1, y_max+1)), outline="white", width=1)
        
        # 2. Draw 'Pill' Tag Label
        tag_text = f" {i+1} "
        # Calculate text bounding box to size the pill
        try:
            tw, th = label_font.getbbox(tag_text)[2:]
        except:
            tw, th = 30, 30

        pill_padding = 6
        pill_rect = [x_min, y_min - th - (pill_padding * 2), x_min + tw + (pill_padding * 2), y_min]
        
        # Ensure pill doesn't go off top of image
        if pill_rect[1] < 0:
            pill_rect[1] = y_min
            pill_rect[3] = y_min + th + (pill_padding * 2)

        # Draw pill background
        draw.rectangle(pill_rect, fill=color)
        # Draw white text on pill
        draw.text((pill_rect[0] + pill_padding, pill_rect[1] + pill_padding), tag_text, fill="white", font=label_font)

    # 3. Create Premium Dark Sidebar
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

    # Sidebar Header
    s_draw.text((width + 30, 30), "ANALYSIS REPORT", fill="#64B5F6", font=title_font)
    s_draw.line((width + 30, 30 + title_size + 10, width + 470, 30 + title_size + 10), fill="#2C2C3E", width=2)

    current_y = 60 + title_size * 2
    for i, bbox in enumerate(boxes):
        color = VIBRANT_COLORS[i % len(VIBRANT_COLORS)]
        label = bbox.get("label", "Unknown Object")
        
        # Draw Badge Number
        badge_w, badge_h = 45, 45
        s_draw.rounded_rectangle([width + 30, current_y, width + 30 + badge_w, current_y + badge_h], radius=8, fill=color)
        s_draw.text((width + 42, current_y + 8), str(i+1), fill="white", font=body_font)
        
        # Draw Label Text (simplified wrapping for demo)
        text_x = width + 90
        display_text = label[:45] + "..." if len(label) > 45 else label
        s_draw.text((text_x, current_y + 8), display_text, fill="#E0E0E0", font=body_font)
        
        current_y += int(badge_h * 1.6)

    output = io.BytesIO()
    combined.save(output, format="JPEG", quality=95)
    return output.getvalue()

def upload_to_gcs(data: bytes, bucket_name: str, blob_name: str, content_type: str = "image/jpeg"):
    """Uploads bytes to GCS and returns the public URL (if configured) or gs:// path."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data, content_type=content_type)
    return f"https://storage.googleapis.com/{bucket_name}/{blob_name}"

def insert_to_bq(rows: List[Dict[str, Any]], dataset_id: str, table_id: str):
    """Inserts rows into BigQuery."""
    client = bigquery.Client()
    table_ref = f"{client.project}.{dataset_id}.{table_id}"
    errors = client.insert_rows_json(table_ref, rows)
    if errors:
        raise Exception(f"BQ Insert errors: {errors}")
