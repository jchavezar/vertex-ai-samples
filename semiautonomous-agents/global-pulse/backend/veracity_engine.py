"""
Veracity Engine — The "gems" algorithm for Global Pulse.

Scores news veracity based on source tiers, cross-referencing,
geographic diversity, bias balance, and signal consistency.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Source tier databases
# ---------------------------------------------------------------------------

TIER_1_SOURCES: dict[str, dict] = {
    "reuters": {"country": "United Kingdom", "code": "GB", "bias": "center", "type": "wire", "trust": 95},
    "associated press": {"country": "United States", "code": "US", "bias": "center", "type": "wire", "trust": 95},
    "agence france-presse": {"country": "France", "code": "FR", "bias": "center", "type": "wire", "trust": 93},
    "afp": {"country": "France", "code": "FR", "bias": "center", "type": "wire", "trust": 93},
    "bbc": {"country": "United Kingdom", "code": "GB", "bias": "center-left", "type": "public", "trust": 90},
    "nhk": {"country": "Japan", "code": "JP", "bias": "center", "type": "public", "trust": 90},
    "deutsche welle": {"country": "Germany", "code": "DE", "bias": "center", "type": "public", "trust": 88},
    "dw": {"country": "Germany", "code": "DE", "bias": "center", "type": "public", "trust": 88},
    "france 24": {"country": "France", "code": "FR", "bias": "center", "type": "public", "trust": 87},
    "al jazeera": {"country": "Qatar", "code": "QA", "bias": "center", "type": "public", "trust": 82},
    "abc australia": {"country": "Australia", "code": "AU", "bias": "center", "type": "public", "trust": 88},
    "abc news australia": {"country": "Australia", "code": "AU", "bias": "center", "type": "public", "trust": 88},
}

TIER_2_SOURCES: dict[str, dict] = {
    "the guardian": {"country": "United Kingdom", "code": "GB", "bias": "center-left", "type": "newspaper", "trust": 82},
    "le monde": {"country": "France", "code": "FR", "bias": "center-left", "type": "newspaper", "trust": 85},
    "der spiegel": {"country": "Germany", "code": "DE", "bias": "center-left", "type": "newspaper", "trust": 83},
    "el país": {"country": "Spain", "code": "ES", "bias": "center-left", "type": "newspaper", "trust": 82},
    "el pais": {"country": "Spain", "code": "ES", "bias": "center-left", "type": "newspaper", "trust": 82},
    "the hindu": {"country": "India", "code": "IN", "bias": "center", "type": "newspaper", "trust": 80},
    "south china morning post": {"country": "Hong Kong", "code": "HK", "bias": "center", "type": "newspaper", "trust": 78},
    "scmp": {"country": "Hong Kong", "code": "HK", "bias": "center", "type": "newspaper", "trust": 78},
    "haaretz": {"country": "Israel", "code": "IL", "bias": "center-left", "type": "newspaper", "trust": 80},
    "nikkei": {"country": "Japan", "code": "JP", "bias": "center", "type": "newspaper", "trust": 83},
    "the globe and mail": {"country": "Canada", "code": "CA", "bias": "center", "type": "newspaper", "trust": 82},
    "times of india": {"country": "India", "code": "IN", "bias": "center", "type": "newspaper", "trust": 75},
    "o globo": {"country": "Brazil", "code": "BR", "bias": "center-right", "type": "newspaper", "trust": 75},
    "the straits times": {"country": "Singapore", "code": "SG", "bias": "center", "type": "newspaper", "trust": 78},
    "daily nation": {"country": "Kenya", "code": "KE", "bias": "center", "type": "newspaper", "trust": 72},
    "new york times": {"country": "United States", "code": "US", "bias": "center-left", "type": "newspaper", "trust": 82},
    "washington post": {"country": "United States", "code": "US", "bias": "center-left", "type": "newspaper", "trust": 80},
    "the economist": {"country": "United Kingdom", "code": "GB", "bias": "center", "type": "magazine", "trust": 88},
    "financial times": {"country": "United Kingdom", "code": "GB", "bias": "center-right", "type": "newspaper", "trust": 87},
    "corriere della sera": {"country": "Italy", "code": "IT", "bias": "center", "type": "newspaper", "trust": 78},
    "asahi shimbun": {"country": "Japan", "code": "JP", "bias": "center-left", "type": "newspaper", "trust": 80},
    "the australian": {"country": "Australia", "code": "AU", "bias": "center-right", "type": "newspaper", "trust": 75},
    "taipei times": {"country": "Taiwan", "code": "TW", "bias": "center", "type": "newspaper", "trust": 74},
    "dawn": {"country": "Pakistan", "code": "PK", "bias": "center", "type": "newspaper", "trust": 72},
    "the daily star": {"country": "Bangladesh", "code": "BD", "bias": "center", "type": "newspaper", "trust": 68},
    "nation africa": {"country": "Kenya", "code": "KE", "bias": "center", "type": "newspaper", "trust": 70},
}

TIER_3_SOURCES: dict[str, dict] = {
    "rt": {"country": "Russia", "code": "RU", "bias": "state-controlled", "type": "state", "trust": 35},
    "xinhua": {"country": "China", "code": "CN", "bias": "state-controlled", "type": "state", "trust": 40},
    "cgtn": {"country": "China", "code": "CN", "bias": "state-controlled", "type": "state", "trust": 38},
    "press tv": {"country": "Iran", "code": "IR", "bias": "state-controlled", "type": "state", "trust": 30},
    "sputnik": {"country": "Russia", "code": "RU", "bias": "state-controlled", "type": "state", "trust": 25},
    "fox news": {"country": "United States", "code": "US", "bias": "right", "type": "cable", "trust": 55},
    "msnbc": {"country": "United States", "code": "US", "bias": "left", "type": "cable", "trust": 55},
    "daily mail": {"country": "United Kingdom", "code": "GB", "bias": "right", "type": "tabloid", "trust": 45},
    "breitbart": {"country": "United States", "code": "US", "bias": "far-right", "type": "digital", "trust": 25},
    "the intercept": {"country": "United States", "code": "US", "bias": "left", "type": "digital", "trust": 65},
    "global times": {"country": "China", "code": "CN", "bias": "state-controlled", "type": "state", "trust": 35},
    "tass": {"country": "Russia", "code": "RU", "bias": "state-controlled", "type": "state", "trust": 30},
    "kcna": {"country": "North Korea", "code": "KP", "bias": "state-controlled", "type": "state", "trust": 10},
}

SIGNAL_TYPES: dict[str, dict] = {
    "BREAKING":    {"color": "#ef4444", "icon": "zap",            "weight": 1.0, "description": "Just happened, limited verification"},
    "DEVELOPING":  {"color": "#f59e0b", "icon": "clock",          "weight": 0.8, "description": "Story still unfolding"},
    "CONFIRMED":   {"color": "#22c55e", "icon": "check-circle",   "weight": 1.2, "description": "Multiple sources verified"},
    "DISPUTED":    {"color": "#f97316", "icon": "alert-triangle",  "weight": 0.5, "description": "Conflicting reports"},
    "ANALYSIS":    {"color": "#8b5cf6", "icon": "brain",           "weight": 0.9, "description": "Expert analysis / opinion"},
    "RETRACTED":   {"color": "#6b7280", "icon": "x-circle",        "weight": 0.1, "description": "Previously reported, now withdrawn"},
}

BIAS_SPECTRUM = [
    "far-left", "left", "center-left", "center",
    "center-right", "right", "far-right", "state-controlled",
]

COUNTRY_FLAGS: dict[str, str] = {
    "US": "🇺🇸", "GB": "🇬🇧", "FR": "🇫🇷", "DE": "🇩🇪", "JP": "🇯🇵",
    "IN": "🇮🇳", "BR": "🇧🇷", "AU": "🇦🇺", "QA": "🇶🇦", "IL": "🇮🇱",
    "ES": "🇪🇸", "CA": "🇨🇦", "HK": "🇭🇰", "SG": "🇸🇬", "KE": "🇰🇪",
    "CN": "🇨🇳", "RU": "🇷🇺", "IR": "🇮🇷", "ZA": "🇿🇦", "MX": "🇲🇽",
    "KR": "🇰🇷", "EG": "🇪🇬", "NG": "🇳🇬", "AR": "🇦🇷", "SE": "🇸🇪",
    "NO": "🇳🇴", "NL": "🇳🇱", "IT": "🇮🇹", "TR": "🇹🇷", "SA": "🇸🇦",
    "PL": "🇵🇱", "CO": "🇨🇴", "TH": "🇹🇭", "PH": "🇵🇭", "ID": "🇮🇩",
    "MY": "🇲🇾", "PK": "🇵🇰", "BD": "🇧🇩", "VN": "🇻🇳", "UA": "🇺🇦",
    "TW": "🇹🇼", "KP": "🇰🇵", "CL": "🇨🇱", "PE": "🇵🇪", "CZ": "🇨🇿",
}


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def classify_source(source_name: str) -> dict:
    """Identify tier, country, bias, and trust score for a source."""
    name = source_name.lower().strip()
    for db, tier in [(TIER_1_SOURCES, 1), (TIER_2_SOURCES, 2), (TIER_3_SOURCES, 3)]:
        for key, meta in db.items():
            if key in name or name in key:
                return {**meta, "tier": tier, "matched_key": key}
    return {
        "country": "Unknown",
        "code": "XX",
        "bias": "unknown",
        "type": "unknown",
        "trust": 50,
        "tier": 2,
        "matched_key": None,
    }


def compute_veracity_score(sources: list[dict]) -> dict:
    """
    Compute an overall veracity score (0-100) for a set of sources
    covering the same topic. This is the "gems" algorithm.
    """
    if not sources:
        return {"score": 0, "confidence": "low", "breakdown": {}, "bias_distribution": {}}

    score = 50
    breakdown: dict[str, int] = {}

    # --- 1. Source tier bonus ---
    tiers = [s.get("tier", 2) for s in sources]
    t1_ratio = tiers.count(1) / len(tiers)
    t3_ratio = tiers.count(3) / len(tiers)
    if t1_ratio >= 0.4:
        tier_bonus = 20
    elif t1_ratio >= 0.2:
        tier_bonus = 12
    else:
        tier_bonus = 5
    tier_bonus -= int(t3_ratio * 15)
    breakdown["source_tier"] = tier_bonus
    score += tier_bonus

    # --- 2. Cross-reference bonus ---
    unique_sources = len({s.get("source_name", "").lower() for s in sources})
    xref_bonus = min(unique_sources * 3, 25)
    breakdown["cross_reference"] = xref_bonus
    score += xref_bonus

    # --- 3. Geographic diversity ---
    unique_countries = {s.get("country_code", "XX") for s in sources}
    geo_bonus = min(len(unique_countries) * 3, 15)
    breakdown["geographic_diversity"] = geo_bonus
    score += geo_bonus

    # --- 4. Language diversity ---
    unique_langs = {s.get("language_original", "en").lower() for s in sources}
    lang_bonus = min(len(unique_langs) * 3, 12)
    breakdown["language_diversity"] = lang_bonus
    score += lang_bonus

    # --- 5. Bias balance ---
    biases = [s.get("bias", "unknown") for s in sources]
    bias_set = {b for b in biases if b != "unknown"}
    if len(bias_set) >= 4:
        bias_bonus = 10
    elif len(bias_set) >= 3:
        bias_bonus = 5
    elif len(bias_set) <= 1 and len(sources) > 3:
        bias_bonus = -15
    else:
        bias_bonus = 0
    breakdown["bias_balance"] = bias_bonus
    score += bias_bonus

    # --- 6. Signal consistency ---
    signals = [s.get("signal_type", "ANALYSIS") for s in sources]
    signal_set = set(signals)
    if "RETRACTED" in signal_set:
        sig_bonus = -15
    elif "DISPUTED" in signal_set and "CONFIRMED" in signal_set:
        sig_bonus = -5
    elif len(signal_set) == 1 and signals[0] == "CONFIRMED":
        sig_bonus = 10
    elif len(signal_set) <= 2:
        sig_bonus = 5
    else:
        sig_bonus = 0
    breakdown["signal_consistency"] = sig_bonus
    score += sig_bonus

    # --- 7. State media penalty ---
    state_count = sum(1 for s in sources if s.get("bias") == "state-controlled")
    state_penalty = -min(state_count * 5, 20)
    if state_penalty:
        breakdown["state_media_penalty"] = state_penalty
        score += state_penalty

    # Clamp
    score = max(0, min(100, score))

    # Confidence
    if unique_sources >= 10 and len(unique_countries) >= 5:
        confidence = "high"
    elif unique_sources >= 5 and len(unique_countries) >= 3:
        confidence = "medium"
    else:
        confidence = "low"

    # Bias distribution
    bias_distribution: dict[str, int] = {}
    for b in biases:
        bias_distribution[b] = bias_distribution.get(b, 0) + 1

    return {
        "score": score,
        "confidence": confidence,
        "breakdown": breakdown,
        "bias_distribution": bias_distribution,
    }


def detect_signals(sources: list[dict]) -> list[dict]:
    """Detect aggregate signals across all sources."""
    signal_counts: dict[str, int] = {}
    for s in sources:
        st = s.get("signal_type", "ANALYSIS")
        signal_counts[st] = signal_counts.get(st, 0) + 1

    total = len(sources) or 1
    detected: list[dict] = []
    for sig_type, count in sorted(signal_counts.items(), key=lambda x: -x[1]):
        meta = SIGNAL_TYPES.get(sig_type, SIGNAL_TYPES["ANALYSIS"])
        confidence = round(count / total * 100)
        detected.append({
            "type": sig_type,
            "confidence": confidence,
            "count": count,
            "evidence": f"{count}/{total} sources classify as {sig_type}",
            "color": meta["color"],
            "icon": meta["icon"],
            "description": meta["description"],
        })
    return detected


def compute_diversity_radar(sources: list[dict]) -> dict:
    """Compute 5-dimension radar scores (0-100 each)."""
    if not sources:
        return {k: 0 for k in ["geographic_reach", "source_quality", "temporal_coverage", "perspective_balance", "depth"]}

    total = len(sources)

    # Geographic reach: countries / max expected (15)
    countries = {s.get("country_code", "XX") for s in sources}
    geographic_reach = min(int(len(countries) / 15 * 100), 100)

    # Source quality: average trust score
    trust_scores = [s.get("trust_score", 50) for s in sources]
    source_quality = int(sum(trust_scores) / len(trust_scores))

    # Temporal coverage: spread based on signal diversity
    signal_set = {s.get("signal_type", "ANALYSIS") for s in sources}
    temporal_coverage = min(int(len(signal_set) / 4 * 100), 100)

    # Perspective balance: bias diversity / max bias categories
    biases = {s.get("bias", "unknown") for s in sources} - {"unknown"}
    perspective_balance = min(int(len(biases) / 5 * 100), 100)

    # Depth: ratio of ANALYSIS/CONFIRMED vs BREAKING
    deep = sum(1 for s in sources if s.get("signal_type") in ("ANALYSIS", "CONFIRMED"))
    depth = int(deep / total * 100)

    return {
        "geographic_reach": geographic_reach,
        "source_quality": source_quality,
        "temporal_coverage": temporal_coverage,
        "perspective_balance": perspective_balance,
        "depth": depth,
    }


def enrich_source(source: dict) -> dict:
    """Add tier/trust/bias/flag metadata to a raw source."""
    classification = classify_source(source.get("source_name", ""))
    source["tier"] = classification["tier"]
    source["trust_score"] = classification["trust"]
    source["bias"] = classification.get("bias", source.get("bias", "unknown"))
    source["flag"] = COUNTRY_FLAGS.get(source.get("country_code", "XX"), "🌐")
    if not source.get("country"):
        source["country"] = classification["country"]
    if not source.get("country_code") or source["country_code"] == "XX":
        source["country_code"] = classification["code"]
        source["flag"] = COUNTRY_FLAGS.get(classification["code"], "🌐")
    return source
