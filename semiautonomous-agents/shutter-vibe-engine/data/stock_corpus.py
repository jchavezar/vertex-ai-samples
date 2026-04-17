"""Synthetic Shutterstock-like corpus.

Each asset has a caption in the contributor-tagging style that we'd see across
Shutterstock.com, Pond5, TurboSquid, PremiumBeat and Editorial. We avoid the
literal words used in the demo queries so we can prove embeddings retrieve by
*meaning*, not keyword overlap.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    asset_id: str
    kind: str  # photo | video | 3d | music | editorial | gif | template
    catalog: str  # shutterstock | pond5 | turbosquid | premiumbeat | editorial | giphy | envato
    caption: str
    tags: tuple[str, ...]


CORPUS: list[Asset] = [
    # ---- Coffee / cozy / nostalgia adjacent ---------------------------------
    Asset("SS-00001", "photo", "shutterstock",
          "Steam rising from a ceramic mug placed on a worn wooden table by a "
          "rain-streaked window in an old European cafe at dawn.",
          ("coffee", "rain", "morning", "wood", "cafe")),
    Asset("SS-00002", "photo", "shutterstock",
          "Friends in their twenties laughing over espresso and pastries in a "
          "sunlit Brooklyn coffee bar, golden-hour light, candid lifestyle.",
          ("friends", "coffee", "lifestyle", "candid", "brooklyn")),
    Asset("SS-00003", "photo", "shutterstock",
          "A single barista's hand pulling a perfect espresso shot, "
          "macro photograph, rich brown crema, dramatic side lighting.",
          ("barista", "espresso", "macro", "craft")),

    # ---- Calm before the storm / weather drama -------------------------------
    Asset("SS-00010", "photo", "shutterstock",
          "Lone fisherman on an empty pier under heavy purple clouds, "
          "ominous Atlantic horizon, wide cinematic composition.",
          ("ocean", "storm", "solitude", "moody")),
    Asset("SS-00011", "video", "pond5",
          "Drone footage of wheat fields bending under sudden wind ahead of a "
          "summer thunderstorm in Kansas, slow push-in, 4K 24fps.",
          ("drone", "weather", "agriculture", "midwest")),
    Asset("SS-00012", "photo", "editorial",
          "Hurricane evacuation route signage swaying as palms whip in early "
          "tropical-storm gusts, Florida coast, photojournalism style.",
          ("hurricane", "evacuation", "news", "florida")),

    # ---- Sustainability / Gen-Z / beach ---------------------------------------
    Asset("SS-00020", "photo", "shutterstock",
          "Diverse group of teenagers picking up plastic bottles on a Pacific "
          "beach at sunrise, reusable bags, smiling, documentary lifestyle.",
          ("sustainability", "youth", "beach", "cleanup", "gen-z")),
    Asset("SS-00021", "video", "pond5",
          "Slow-motion clip of biodegradable cup dissolving in seawater, "
          "macro underwater shot, soft natural light, eco-marketing ready.",
          ("eco", "macro", "ocean", "biodegradable")),
    Asset("SS-00022", "photo", "shutterstock",
          "Two Gen-Z athletes practising basketball at sunset on a refurbished "
          "Los Angeles community court, sweat, grain, vibrant graffiti walls.",
          ("basketball", "gen-z", "urban", "athletics", "sunset")),

    # ---- Brand-style / retro / Wes-Anderson-y --------------------------------
    Asset("SS-00030", "photo", "offset",
          "Symmetrical pastel hotel facade, mint green and salmon pink, single "
          "bellboy centred in frame, Wes-Anderson-inspired storytelling shot.",
          ("symmetry", "pastel", "cinematic", "retro")),
    Asset("SS-00031", "photo", "shutterstock",
          "Vintage 1970s VW camper van parked on a Californian highway shoulder "
          "during golden hour, faded film grain, road-trip nostalgia.",
          ("vintage", "road-trip", "70s", "film")),

    # ---- Brand-safety challenges (alcohol, gambling, weapons) ---------------
    Asset("SS-00040", "photo", "shutterstock",
          "Close-up of an old-fashioned cocktail with bourbon, bitters and an "
          "orange peel twist on a polished bar, low-key lighting.",
          ("cocktail", "bourbon", "bar", "alcohol")),
    Asset("SS-00041", "photo", "shutterstock",
          "Roulette wheel mid-spin in a luxury Monaco casino, blurred chips, "
          "bokeh chandeliers, gambling lifestyle.",
          ("casino", "roulette", "gambling")),
    Asset("SS-00042", "editorial", "editorial",
          "Police evidence photograph of a recovered handgun on a forensic "
          "table, neutral grey backdrop, news-wire style.",
          ("crime", "weapon", "news")),
    Asset("SS-00043", "photo", "shutterstock",
          "Family of four enjoying a healthy summer picnic with fresh fruit "
          "and lemonade in a sunny city park.",
          ("family", "park", "summer", "wholesome")),

    # ---- Music / B-roll matching ---------------------------------------------
    Asset("SS-00050", "music", "premiumbeat",
          "Uplifting indie-folk acoustic guitar instrumental, warm major key, "
          "claps and stomps, 110bpm, ideal for travel and outdoor brand films.",
          ("indie", "acoustic", "uplifting", "travel")),
    Asset("SS-00051", "music", "premiumbeat",
          "Brooding cinematic orchestral cue with low strings and timpani, "
          "tension building under news-style narration, 80bpm.",
          ("cinematic", "tension", "news", "orchestral")),
    Asset("SS-00052", "video", "pond5",
          "Aerial drone reveal of a backpacker walking a Patagonian mountain "
          "ridge at sunrise, sweeping vista, 4K HDR.",
          ("travel", "drone", "patagonia", "outdoor")),

    # ---- 3D and templates ----------------------------------------------------
    Asset("SS-00060", "3d", "turbosquid",
          "Photorealistic 3D model of a minimalist Scandinavian living room, "
          "textured oak floor, north-facing window light, ready for arch-viz.",
          ("3d", "interior", "scandinavian", "archviz")),
    Asset("SS-00061", "template", "envato",
          "Editable Adobe After Effects mogrt of a clean lower-third for "
          "corporate keynote videos, smooth ease-out animation.",
          ("template", "aftereffects", "lower-third", "corporate")),

    # ---- Editorial moments ----------------------------------------------------
    Asset("SS-00070", "editorial", "editorial",
          "Climate protesters holding hand-painted signs in front of EU "
          "Parliament during a youth-led march, photojournalism, Brussels.",
          ("climate", "protest", "youth", "brussels")),
    Asset("SS-00071", "editorial", "editorial",
          "Astronaut waving from the open hatch of a SpaceX Crew Dragon "
          "capsule moments after splashdown in the Gulf of Mexico.",
          ("space", "spacex", "splashdown", "news")),

    # ---- Multilingual targets (the captions stay English; queries vary) -----
    Asset("SS-00080", "photo", "shutterstock",
          "Senior couple dancing tango on a cobblestone Buenos Aires street at "
          "twilight, soft window light, intimate cultural moment.",
          ("tango", "couple", "buenos-aires", "culture")),
    Asset("SS-00081", "photo", "shutterstock",
          "Traditional Japanese tea ceremony, hands pouring matcha into a "
          "ceramic bowl, tatami mat, restrained composition.",
          ("matcha", "tea-ceremony", "japan", "minimal")),
    Asset("SS-00082", "photo", "shutterstock",
          "Bavarian Oktoberfest beer hall full of guests in lederhosen "
          "raising steins, joyful crowd, colourful banners.",
          ("oktoberfest", "germany", "festival", "crowd")),
    Asset("SS-00083", "photo", "shutterstock",
          "Spice merchant arranging colourful bowls of saffron, sumac and "
          "cardamom in a Marrakech souk, golden afternoon light.",
          ("spices", "morocco", "market", "culture")),

    # ---- More texture / abstract / mood --------------------------------------
    Asset("SS-00090", "photo", "shutterstock",
          "Abstract macro photograph of oil and water droplets refracting "
          "neon pink and blue light, modern editorial background texture.",
          ("abstract", "macro", "neon", "texture")),
    Asset("SS-00091", "photo", "shutterstock",
          "Crumpled brown kraft paper lit from one side, soft shadows, "
          "minimalist organic background plate for product shots.",
          ("paper", "minimal", "background", "product")),
]


def by_kind(kind: str) -> list[Asset]:
    return [a for a in CORPUS if a.kind == kind]


if __name__ == "__main__":  # pragma: no cover
    print(f"Corpus size: {len(CORPUS)}")
    from collections import Counter
    print("By kind:", Counter(a.kind for a in CORPUS))
    print("By catalog:", Counter(a.catalog for a in CORPUS))
