"""
Vibe Engine — Underground score computation and vibe tagging.
Deterministic logic separate from AI reasoning.
"""

# Known chain restaurants/cafes that should be penalized
KNOWN_CHAINS = [
    "starbucks", "dunkin", "mcdonald", "subway", "chipotle",
    "sweetgreen", "blue bottle", "gregorys", "joe coffee",
    "panera", "shake shack", "chick-fil-a", "five guys",
    "pret a manger", "le pain quotidien", "cosi", "au bon pain"
]

# Vibe aesthetic tags
AESTHETIC_TAGS = [
    "contemporary", "cozy", "industrial", "minimal", "eclectic",
    "vintage", "bright", "dark", "intimate", "spacious"
]


def compute_underground_score(venue: dict, web_signals: dict = None) -> int:
    """
    Compute underground score (0-100) for a venue.
    Higher = more underground/local gem, Lower = mainstream/touristy.

    Args:
        venue: Venue dict with name, review_count, rating, etc.
        web_signals: Optional dict with reddit_mentions, listicle_appearances, niche_blog_count

    Returns:
        Underground score from 0 to 100
    """
    web_signals = web_signals or {}
    score = 100

    # Penalize by review count (popularity != underground)
    review_count = venue.get("review_count", 0)
    if review_count > 2000:
        score -= 50
    elif review_count > 1000:
        score -= 35
    elif review_count > 500:
        score -= 20
    elif review_count > 200:
        score -= 10

    # Penalize chains/franchises
    name_lower = venue.get("name", "").lower()
    if any(chain in name_lower for chain in KNOWN_CHAINS):
        score -= 60

    # Penalize heavy listicle coverage (too mainstream)
    listicle_count = web_signals.get("listicle_appearances", 0)
    if listicle_count > 5:
        score -= 25
    elif listicle_count > 2:
        score -= 10

    # Reward organic Reddit mentions by locals
    reddit_count = web_signals.get("reddit_mentions", 0)
    score += min(reddit_count * 8, 25)

    # Reward niche blog features (not Yelp/TripAdvisor/Timeout)
    niche_blogs = web_signals.get("niche_blog_count", 0)
    score += min(niche_blogs * 5, 15)

    # Reward low review count with high rating (hidden gem signal)
    if review_count < 100 and venue.get("rating", 0) >= 4.0:
        score += 15

    # Clamp to 0-100
    return max(0, min(100, score))


def tag_aesthetic(venue: dict, agent_analysis: str = "") -> list[str]:
    """
    Extract aesthetic tags for a venue based on categories and analysis.

    Args:
        venue: Venue dict with categories
        agent_analysis: Optional AI analysis text to extract tags from

    Returns:
        List of 3-5 aesthetic tags
    """
    tags = []
    categories = [c.lower() for c in venue.get("categories", [])]
    name_lower = venue.get("name", "").lower()
    analysis_lower = agent_analysis.lower()

    # Infer from categories
    if any("coffee" in c or "cafe" in c for c in categories):
        tags.append("cozy")
    if any("cocktail" in c or "bar" in c for c in categories):
        tags.append("intimate")
    if any("brewery" in c or "taproom" in c for c in categories):
        tags.append("industrial")
    if any("bakery" in c or "patisserie" in c for c in categories):
        tags.append("bright")

    # Extract from analysis text
    for aesthetic in AESTHETIC_TAGS:
        if aesthetic in analysis_lower and aesthetic not in tags:
            tags.append(aesthetic)

    # Default tags if none found
    if not tags:
        tags = ["contemporary"]

    return tags[:5]


def tag_accessibility(venue: dict, web_signals: dict = None) -> str:
    """
    Determine accessibility level for walk-in visits.

    Args:
        venue: Venue dict with review_count, price
        web_signals: Optional dict with reservation mentions

    Returns:
        One of: "walk-in" | "usually available" | "book ahead" | "impossible to get in"
    """
    web_signals = web_signals or {}
    review_count = venue.get("review_count", 0)
    price = venue.get("price") or ""

    # Check for reservation mentions in web signals
    reservation_mentions = web_signals.get("reservation_mentions", 0)
    if reservation_mentions > 3:
        return "book ahead"

    # High-end places with lots of reviews = hard to get in
    if len(price) >= 3 and review_count > 1000:
        return "impossible to get in"

    if len(price) >= 3 and review_count > 500:
        return "book ahead"

    if review_count > 2000:
        return "usually available"

    # Default for most places
    return "walk-in"


def synthesize_vibe_profile(
    venue: dict,
    web_signals: dict = None,
    agent_analysis: str = ""
) -> dict:
    """
    Create a complete vibe profile for a venue.

    Args:
        venue: Venue dict from Yelp
        web_signals: Web signal data
        agent_analysis: AI analysis text

    Returns:
        Complete vibe profile dict
    """
    return {
        **venue,
        "underground_score": compute_underground_score(venue, web_signals),
        "vibe_tags": tag_aesthetic(venue, agent_analysis),
        "accessibility": tag_accessibility(venue, web_signals),
        "web_signals": web_signals or {},
    }
