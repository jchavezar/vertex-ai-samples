"""
Generate professional architecture diagrams for SharePoint WIF Portal.
White background, Google Docs friendly.
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Ensure output directory exists
os.makedirs("diagrams", exist_ok=True)

# Colors
COLORS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "gray_light": (248, 249, 250),
    "gray_border": (218, 220, 224),
    "gray_text": (95, 99, 104),

    # Google Cloud colors
    "gcp_blue": (66, 133, 244),
    "gcp_green": (52, 168, 83),
    "gcp_yellow": (251, 188, 4),
    "gcp_red": (234, 67, 53),

    # Microsoft colors
    "ms_blue": (0, 120, 212),
    "ms_teal": (0, 183, 195),

    # Framework colors
    "react_blue": (97, 218, 251),
    "fastapi_teal": (0, 150, 136),
    "python_yellow": (255, 212, 59),
}


def load_fonts():
    """Load fonts with fallbacks."""
    paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    regular_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    bold_font = None
    regular_font = None

    for p in paths:
        if os.path.exists(p):
            bold_font = p
            break

    for p in regular_paths:
        if os.path.exists(p):
            regular_font = p
            break

    if bold_font and regular_font:
        return {
            "title": ImageFont.truetype(bold_font, 32),
            "subtitle": ImageFont.truetype(regular_font, 16),
            "header": ImageFont.truetype(bold_font, 16),
            "body": ImageFont.truetype(regular_font, 13),
            "small": ImageFont.truetype(regular_font, 11),
        }

    default = ImageFont.load_default()
    return {"title": default, "subtitle": default, "header": default, "body": default, "small": default}


FONTS = load_fonts()


def draw_rounded_rect(draw, coords, radius, fill, outline=None, width=2):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = coords
    diameter = radius * 2

    # Main body
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

    # Corners
    draw.ellipse([x1, y1, x1 + diameter, y1 + diameter], fill=fill)
    draw.ellipse([x2 - diameter, y1, x2, y1 + diameter], fill=fill)
    draw.ellipse([x1, y2 - diameter, x1 + diameter, y2], fill=fill)
    draw.ellipse([x2 - diameter, y2 - diameter, x2, y2], fill=fill)

    if outline:
        # Top and bottom lines
        draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=width)
        draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline, width=width)
        # Left and right lines
        draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline, width=width)
        draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=width)
        # Corner arcs
        draw.arc([x1, y1, x1 + diameter, y1 + diameter], 180, 270, fill=outline, width=width)
        draw.arc([x2 - diameter, y1, x2, y1 + diameter], 270, 360, fill=outline, width=width)
        draw.arc([x1, y2 - diameter, x1 + diameter, y2], 90, 180, fill=outline, width=width)
        draw.arc([x2 - diameter, y2 - diameter, x2, y2], 0, 90, fill=outline, width=width)


def draw_box(draw, x, y, w, h, label, sublabel=None, color=COLORS["gcp_blue"], text_color=None):
    """Draw a labeled box with optional sublabel."""
    # Auto text color based on background brightness
    if text_color is None:
        brightness = (color[0] * 299 + color[1] * 587 + color[2] * 114) / 1000
        text_color = COLORS["black"] if brightness > 150 else COLORS["white"]

    draw_rounded_rect(draw, (x, y, x + w, y + h), 6, fill=color)

    # Render text
    lines = label.split("\n")
    total_height = len(lines) * 18
    if sublabel:
        total_height += 14

    start_y = y + (h - total_height) / 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=FONTS["header"])
        tw = bbox[2] - bbox[0]
        draw.text((x + (w - tw) / 2, start_y + i * 18), line, fill=text_color, font=FONTS["header"])

    if sublabel:
        bbox = draw.textbbox((0, 0), sublabel, font=FONTS["small"])
        tw = bbox[2] - bbox[0]
        draw.text((x + (w - tw) / 2, start_y + len(lines) * 18 + 2), sublabel,
                  fill=text_color, font=FONTS["small"])


def draw_arrow(draw, start, end, color=COLORS["gray_text"], width=2, dashed=False):
    """Draw an arrow from start to end with proper arrowhead."""
    if dashed:
        # Draw dashed line
        length = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        dash_len = 8
        gap_len = 4
        dx = (end[0] - start[0]) / length
        dy = (end[1] - start[1]) / length

        pos = 0
        while pos < length - 15:
            x1 = start[0] + dx * pos
            y1 = start[1] + dy * pos
            x2 = start[0] + dx * min(pos + dash_len, length - 15)
            y2 = start[1] + dy * min(pos + dash_len, length - 15)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
            pos += dash_len + gap_len
    else:
        draw.line([start, end], fill=color, width=width)

    # Arrowhead
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    arrow_len = 12
    arrow_angle = math.pi / 6

    x1 = end[0] - arrow_len * math.cos(angle - arrow_angle)
    y1 = end[1] - arrow_len * math.sin(angle - arrow_angle)
    x2 = end[0] - arrow_len * math.cos(angle + arrow_angle)
    y2 = end[1] - arrow_len * math.sin(angle + arrow_angle)

    draw.polygon([end, (x1, y1), (x2, y2)], fill=color)


def draw_section_label(draw, x, y, label, color):
    """Draw a section label."""
    bbox = draw.textbbox((0, 0), label, font=FONTS["header"])
    tw = bbox[2] - bbox[0]

    # Background pill
    draw_rounded_rect(draw, (x - 5, y - 2, x + tw + 10, y + 20), 4, fill=color)
    draw.text((x, y), label, fill=COLORS["white"], font=FONTS["header"])


def create_main_architecture():
    """Create the main architecture diagram - clean, professional, white background."""
    width, height = 1400, 950
    img = Image.new('RGB', (width, height), COLORS["white"])
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((50, 25), "SharePoint WIF Portal", fill=COLORS["black"], font=FONTS["title"])
    draw.text((50, 65), "Enterprise Search with Federated Identity & Per-User ACL Enforcement",
              fill=COLORS["gray_text"], font=FONTS["subtitle"])

    # === ROW 1: USER INTERFACES ===
    y1 = 120
    draw_section_label(draw, 50, y1, "User Interfaces", COLORS["gcp_blue"])

    draw_box(draw, 50, y1 + 35, 180, 70, "Custom Portal", "React 19 + Vite 8", COLORS["react_blue"])
    draw_box(draw, 250, y1 + 35, 180, 70, "Gemini Enterprise", "Agentspace UI", COLORS["gcp_blue"])
    draw_box(draw, 450, y1 + 35, 180, 70, "Test UI", "FastAPI Static", COLORS["fastapi_teal"])

    # === ROW 1: MICROSOFT ENTRA ===
    draw_section_label(draw, 700, y1, "Microsoft Entra ID", COLORS["ms_blue"])

    draw_box(draw, 700, y1 + 35, 200, 70, "App Registration", "OAuth 2.0 / OIDC", COLORS["ms_blue"])
    draw_box(draw, 920, y1 + 35, 200, 70, "Token Issuance", "ID Token + Access Token", COLORS["ms_teal"])

    # === ROW 2: WIF + STS ===
    y2 = 280
    draw_section_label(draw, 50, y2, "Workforce Identity Federation", COLORS["gcp_green"])

    draw_box(draw, 50, y2 + 35, 260, 70, "ge-login-provider", "aud: {client-id}", COLORS["gcp_green"])
    draw_box(draw, 330, y2 + 35, 260, 70, "entra-provider", "aud: api://{client-id}", COLORS["gcp_green"])

    draw_section_label(draw, 700, y2, "Security Token Service", COLORS["gcp_yellow"])
    draw_box(draw, 700, y2 + 35, 200, 70, "Google STS", "Token Exchange", COLORS["gcp_yellow"])

    # === ROW 3: BACKEND SERVICES ===
    y3 = 430
    draw_section_label(draw, 50, y3, "Backend Services", COLORS["fastapi_teal"])

    draw_box(draw, 50, y3 + 35, 260, 90, "FastAPI Backend", "Python 3.12 + Uvicorn", COLORS["fastapi_teal"])

    # API endpoints
    endpoints = ["/api/chat", "/api/quick", "/api/sessions"]
    for i, ep in enumerate(endpoints):
        draw.text((70, y3 + 80 + i * 14), ep, fill=COLORS["white"], font=FONTS["small"])

    draw_box(draw, 330, y3 + 35, 260, 90, "ADK Agent", "InsightComparator", COLORS["python_yellow"])
    draw.text((350, y3 + 85), "compare_insights tool", fill=COLORS["black"], font=FONTS["small"])
    draw.text((350, y3 + 100), "SharePoint + Web search", fill=COLORS["black"], font=FONTS["small"])

    # === ROW 3: GCP AI SERVICES ===
    draw_section_label(draw, 700, y3, "Google Cloud AI", COLORS["gcp_red"])

    draw_box(draw, 700, y3 + 35, 200, 90, "Discovery Engine", "streamAssist API", COLORS["gcp_red"])
    draw_box(draw, 920, y3 + 35, 200, 90, "Agent Engine", "Vertex AI ADK", COLORS["gcp_red"])

    # === ROW 4: DATA SOURCES ===
    y4 = 600
    draw_section_label(draw, 50, y4, "Data Sources", COLORS["ms_blue"])

    draw_box(draw, 50, y4 + 35, 260, 80, "SharePoint Online", "Federated Connector", COLORS["ms_blue"])
    draw.text((70, y4 + 85), "Per-user ACL enforcement", fill=COLORS["white"], font=FONTS["small"])

    draw_box(draw, 330, y4 + 35, 260, 80, "Google Search", "Gemini Grounding", COLORS["gcp_blue"])
    draw.text((350, y4 + 85), "Public web results", fill=COLORS["white"], font=FONTS["small"])

    # === ROW 4: DEPLOYMENT ===
    draw_section_label(draw, 700, y4, "Deployment", COLORS["gcp_blue"])

    draw_box(draw, 700, y4 + 35, 130, 80, "Cloud Run", "Containers", COLORS["gcp_blue"])
    draw_box(draw, 845, y4 + 35, 130, 80, "IAP", "Access Control", COLORS["gcp_blue"])
    draw_box(draw, 990, y4 + 35, 130, 80, "GLB", "Load Balancer", COLORS["gcp_blue"])

    # === ARROWS ===
    arrow_color = COLORS["gray_text"]

    # User interfaces -> Entra
    draw_arrow(draw, (630, y1 + 70), (700, y1 + 70), arrow_color)

    # Entra -> WIF providers
    draw_arrow(draw, (800, y1 + 105), (180, y2 + 35), arrow_color)
    draw_arrow(draw, (800, y1 + 105), (460, y2 + 35), arrow_color)

    # WIF -> STS
    draw_arrow(draw, (310, y2 + 70), (700, y2 + 70), arrow_color)
    draw_arrow(draw, (590, y2 + 70), (700, y2 + 70), arrow_color)

    # STS -> Backend
    draw_arrow(draw, (800, y2 + 105), (180, y3 + 35), arrow_color)
    draw_arrow(draw, (800, y2 + 105), (460, y3 + 35), arrow_color)

    # Backend -> Discovery/Agent Engine
    draw_arrow(draw, (310, y3 + 80), (700, y3 + 80), arrow_color)
    draw_arrow(draw, (590, y3 + 80), (920, y3 + 80), arrow_color)

    # AI Services -> Data Sources
    draw_arrow(draw, (800, y3 + 125), (180, y4 + 35), arrow_color)
    draw_arrow(draw, (1020, y3 + 125), (460, y4 + 35), arrow_color)

    # === LEGEND ===
    legend_y = 780
    draw.text((50, legend_y), "Legend:", fill=COLORS["black"], font=FONTS["header"])

    legend_items = [
        (COLORS["gcp_blue"], "Google Cloud"),
        (COLORS["ms_blue"], "Microsoft"),
        (COLORS["react_blue"], "Frontend"),
        (COLORS["fastapi_teal"], "Backend"),
        (COLORS["gcp_green"], "Identity"),
        (COLORS["gcp_red"], "AI Services"),
        (COLORS["gcp_yellow"], "Token Exchange"),
    ]

    x_offset = 130
    for color, label in legend_items:
        draw.rectangle([x_offset, legend_y + 2, x_offset + 20, legend_y + 18], fill=color)
        draw.text((x_offset + 28, legend_y), label, fill=COLORS["black"], font=FONTS["body"])
        x_offset += 130

    # === TECH STACK ===
    draw.text((50, 850), "Tech Stack:", fill=COLORS["black"], font=FONTS["header"])

    stack_items = [
        "React 19", "Vite 8", "TypeScript", "MSAL", "FastAPI", "Python 3.12",
        "google-cloud-aiplatform", "ADK", "WIF", "STS", "Cloud Run", "IAP"
    ]

    x_offset = 150
    for item in stack_items:
        bbox = draw.textbbox((0, 0), item, font=FONTS["body"])
        tw = bbox[2] - bbox[0]
        draw_rounded_rect(draw, (x_offset, 850, x_offset + tw + 16, 872), 4,
                          fill=COLORS["gray_light"], outline=COLORS["gray_border"])
        draw.text((x_offset + 8, 852), item, fill=COLORS["black"], font=FONTS["body"])
        x_offset += tw + 26

    img.save("diagrams/architecture_main.png", quality=95)
    print("Generated diagrams/architecture_main.png")


def create_auth_flow():
    """Create authentication flow diagram."""
    width, height = 1200, 600
    img = Image.new('RGB', (width, height), COLORS["white"])
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((50, 25), "Authentication Flow", fill=COLORS["black"], font=FONTS["title"])
    draw.text((50, 60), "WIF Token Exchange: Entra JWT -> GCP Access Token",
              fill=COLORS["gray_text"], font=FONTS["subtitle"])

    # Flow boxes
    y = 150
    box_w, box_h = 180, 90
    gap = 40

    boxes = [
        (50, "User", "Browser", COLORS["gray_light"], COLORS["black"]),
        (50 + box_w + gap, "Entra ID", "JWT Issuer", COLORS["ms_blue"], COLORS["white"]),
        (50 + 2*(box_w + gap), "WIF Provider", "Validate JWT", COLORS["gcp_green"], COLORS["white"]),
        (50 + 3*(box_w + gap), "Google STS", "Exchange Token", COLORS["gcp_yellow"], COLORS["black"]),
        (50 + 4*(box_w + gap), "Discovery Engine", "Query SharePoint", COLORS["gcp_red"], COLORS["white"]),
    ]

    for x, title, subtitle, bg, fg in boxes:
        draw_box(draw, x, y, box_w, box_h, title, subtitle, bg, fg)

    # Arrows with step labels
    arrow_y = y + box_h / 2
    steps = [
        (50 + box_w, 50 + box_w + gap, "1. Login"),
        (50 + box_w + gap + box_w, 50 + 2*(box_w + gap), "2. Get JWT"),
        (50 + 2*(box_w + gap) + box_w, 50 + 3*(box_w + gap), "3. Validate"),
        (50 + 3*(box_w + gap) + box_w, 50 + 4*(box_w + gap), "4. GCP Token"),
    ]

    for x1, x2, label in steps:
        draw_arrow(draw, (x1, arrow_y), (x2, arrow_y), COLORS["gcp_blue"], 3)
        mid_x = (x1 + x2) / 2
        draw.text((mid_x - 25, arrow_y - 25), label, fill=COLORS["gcp_blue"], font=FONTS["body"])

    # Step descriptions
    desc_y = 300
    descriptions = [
        "1. User clicks login in Custom Portal or Gemini Enterprise",
        "2. Entra ID issues JWT with appropriate audience (ID token or Access token)",
        "3. WIF Provider validates JWT signature and maps to GCP principal",
        "4. Google STS exchanges Entra token for short-lived GCP access token",
        "5. Discovery Engine queries SharePoint using user's federated identity",
    ]

    for i, desc in enumerate(descriptions):
        draw.text((50, desc_y + i * 28), desc, fill=COLORS["black"], font=FONTS["body"])

    # Key insight
    insight_y = 470
    draw_rounded_rect(draw, (50, insight_y, 1150, insight_y + 80), 8,
                      fill=COLORS["gray_light"], outline=COLORS["gcp_green"], width=2)

    draw.text((70, insight_y + 12), "Two WIF Providers Required:", fill=COLORS["gcp_green"], font=FONTS["header"])
    draw.text((70, insight_y + 35), "ge-login-provider (aud: {client-id}) - For Gemini Enterprise user login",
              fill=COLORS["black"], font=FONTS["body"])
    draw.text((70, insight_y + 55), "entra-provider (aud: api://{client-id}) - For Agent Engine token exchange",
              fill=COLORS["black"], font=FONTS["body"])

    img.save("diagrams/auth_flow.png", quality=95)
    print("Generated diagrams/auth_flow.png")


def create_tech_stack():
    """Create technology stack diagram."""
    width, height = 1100, 750
    img = Image.new('RGB', (width, height), COLORS["white"])
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((50, 25), "Technology Stack", fill=COLORS["black"], font=FONTS["title"])

    # Three columns
    col_w = 320
    col_gap = 30
    col_x = [50, 50 + col_w + col_gap, 50 + 2 * (col_w + col_gap)]

    # Column headers
    headers = [
        ("Frontend", COLORS["react_blue"]),
        ("Backend", COLORS["fastapi_teal"]),
        ("Google Cloud", COLORS["gcp_blue"]),
    ]

    for i, (title, color) in enumerate(headers):
        draw_section_label(draw, col_x[i], 90, title, color)

    # Frontend items
    frontend = [
        ("React 19", "UI Framework", COLORS["react_blue"]),
        ("Vite 8", "Build Tool", COLORS["react_blue"]),
        ("TypeScript", "Language", COLORS["gray_light"]),
        ("MSAL React", "Microsoft Auth", COLORS["ms_blue"]),
        ("Framer Motion", "Animations", COLORS["gray_light"]),
        ("Lucide React", "Icons", COLORS["gray_light"]),
    ]

    for i, (name, desc, color) in enumerate(frontend):
        y = 130 + i * 55
        draw_box(draw, col_x[0], y, col_w, 45, name, desc, color)

    # Backend items
    backend = [
        ("FastAPI", "Web Framework", COLORS["fastapi_teal"]),
        ("Python 3.12", "Runtime", COLORS["python_yellow"]),
        ("Uvicorn", "ASGI Server", COLORS["gray_light"]),
        ("google-auth", "GCP Authentication", COLORS["gray_light"]),
        ("google-cloud-aiplatform", "Vertex AI SDK", COLORS["gcp_blue"]),
        ("SSE Starlette", "Server-Sent Events", COLORS["gray_light"]),
    ]

    for i, (name, desc, color) in enumerate(backend):
        y = 130 + i * 55
        draw_box(draw, col_x[1], y, col_w, 45, name, desc, color)

    # GCP items
    gcp = [
        ("Discovery Engine", "Search + RAG", COLORS["gcp_red"]),
        ("Agentspace", "Agent UI", COLORS["gcp_red"]),
        ("Agent Engine", "ADK Runtime", COLORS["gcp_yellow"]),
        ("WIF", "Identity Federation", COLORS["gcp_green"]),
        ("Cloud Run", "Container Hosting", COLORS["gcp_blue"]),
        ("IAP", "Identity-Aware Proxy", COLORS["gcp_blue"]),
    ]

    for i, (name, desc, color) in enumerate(gcp):
        y = 130 + i * 55
        draw_box(draw, col_x[2], y, col_w, 45, name, desc, color)

    # Microsoft section
    ms_y = 480
    draw_section_label(draw, 50, ms_y, "Microsoft Azure", COLORS["ms_blue"])

    ms_items = [
        ("Entra ID", "Identity Provider"),
        ("App Registration", "OAuth Configuration"),
        ("SharePoint Online", "Document Storage"),
        ("Graph API", "Data Access"),
    ]

    item_w = 240
    for i, (name, desc) in enumerate(ms_items):
        x = 50 + i * (item_w + 20)
        draw_box(draw, x, ms_y + 35, item_w, 55, name, desc, COLORS["ms_blue"])

    # ADK section
    adk_y = 600
    draw_section_label(draw, 50, adk_y, "Agent Development Kit (ADK)", COLORS["python_yellow"])

    adk_items = [
        ("InsightComparator", "Multi-source Agent"),
        ("compare_insights", "Tool Function"),
        ("Reasoning Engine", "Agent Runtime"),
        ("MCP", "Tool Protocol"),
    ]

    for i, (name, desc) in enumerate(adk_items):
        x = 50 + i * (item_w + 20)
        draw_box(draw, x, adk_y + 35, item_w, 55, name, desc, COLORS["python_yellow"])

    img.save("diagrams/tech_stack.png", quality=95)
    print("Generated diagrams/tech_stack.png")


if __name__ == "__main__":
    create_main_architecture()
    create_auth_flow()
    create_tech_stack()
    print("\nAll diagrams generated in diagrams/")
