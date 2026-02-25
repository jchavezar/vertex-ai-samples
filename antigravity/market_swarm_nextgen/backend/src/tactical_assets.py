import os

# Design System Configuration
TEXTURES = {
    "bullish": "emerald_texture.png",
    "bearish": "obsidian_texture.png",
    "neutral": "grid_texture.png"
}

# Icon Prompt Templates for "Nano Banana 3" style
ICON_PROMPT_TEMPLATE = """
High-end 3D entity icon for {company_name} ({ticker}).
Style: Quantum-finance, matte translucent glass, vibrant {color_accent} accents.
Environment: Floating in obsidian void, studio lighting, 8k resolution.
Shape: Abstract geometric representation of {business_focus}.
"""

BUSINESS_MAPPINGS = {
    "NVDA": {"focus": "parallel compute arcs", "color": "emerald"},
    "AMD": {"focus": "crystalline logic arrays", "color": "ruby"},
    "AAPL": {"focus": "brushed titanium spheres", "color": "silver"},
    "MSFT": {"focus": "iridescent cloud clusters", "color": "azure"},
    "GOOGL": {"focus": "prismatic neural webs", "color": "rainbow"},
    "META": {"focus": "holographic social nodes", "color": "violet"},
    "AMZN": {"focus": "geometric logic ribbons", "color": "amber"}
}

def get_texture_path(momentum: str) -> str:
    if "Bullish" in momentum:
        return TEXTURES["bullish"]
    if "Bearish" in momentum:
        return TEXTURES["bearish"]
    return TEXTURES["neutral"]

def get_icon_prompt(ticker: str, name: str) -> str:
    mapping = BUSINESS_MAPPINGS.get(ticker.upper(), {"focus": "abstract strategic node", "color": "blue"})
    return ICON_PROMPT_TEMPLATE.format(
        company_name=name,
        ticker=ticker,
        color_accent=mapping["color"],
        business_focus=mapping["focus"]
    )
