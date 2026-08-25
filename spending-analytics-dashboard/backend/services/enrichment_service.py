import json
import pandas as pd
import os
import re
from typing import List, Dict, Any

def clean_merchant_name(desc: str) -> str:
    d = str(desc).strip()
    if 'DELTA AIR LINES' in d or 'DELTA' in d: return 'Delta Air Lines'
    if 'NORDSTROM' in d: return 'Nordstrom Direct'
    if 'SEPHORA' in d: return 'Sephora'
    if 'NYU LANGONE' in d: return 'NYU Langone Medical'
    if 'AMAZON' in d or 'AMZN' in d or 'KINDLE' in d or 'PRIME VIDEO' in d:
        if 'TIPS' in d: return 'Amazon Tips'
        if 'GROCERY' in d or 'FRESH' in d: return 'Amazon Fresh'
        if 'KINDLE' in d: return 'Amazon Kindle'
        if 'PRIME' in d: return 'Prime Video'
        return 'Amazon'
    if 'SKIMS' in d: return 'SKIMS'
    if 'SHOPBALA' in d or 'BALA BANGLES' in d or 'BALA' in d: return 'Bala Bangles'
    if 'UBER' in d: return 'Uber / Uber Eats'
    if 'LYFT' in d: return 'Lyft'
    if 'RAPPI' in d: return 'Rappi'
    if 'BLOOMINGDALES' in d: return 'Bloomingdales'
    if 'MACYS' in d or 'MACY' in d: return "Macy's"
    if 'SAKS' in d: return 'Saks Fifth Avenue'
    if 'SISU CLINIC' in d: return 'SISU Clinic'
    if 'SUMMIT MEDICAL' in d: return 'Summit Medical Group'
    if 'MATTRESS FIRM' in d: return 'Mattress Firm'
    if 'CONTAINER' in d: return 'The Container Store'
    if 'MUJI' in d: return 'Muji'
    if 'DICE.FM' in d or 'DICE' in d: return 'DICE.FM Tickets'
    if 'JUST ENERGY' in d: return 'Just Energy'
    if 'HERCULES' in d: return 'Hercules Laundry'
    if 'GRUBHUB' in d:
        if 'MAMAN' in d: return 'Grubhub - Maman'
        if 'BLUES' in d or 'BLUESTONE' in d: return 'Grubhub - Bluestone Lane'
        if 'WHITE' in d: return 'Grubhub - White Maize'
        if 'GHPLUS' in d or 'PLUS' in d: return 'Grubhub Plus'
        if '5NAPK' in d: return 'Grubhub - 5 Napkin Burger'
        if 'PEPEGIALLO' in d: return 'Grubhub - Pepe Giallo'
        if 'BIRRI' in d: return 'Grubhub - Birria'
        return 'Grubhub'
    if 'WHOLE' in d or 'WHOLEFDS' in d: return 'Whole Foods Market'
    if 'DOORDASH' in d or 'DD *' in d:
        if 'PETS' in d: return 'DoorDash - PetSmart'
        if 'BLUEST' in d: return 'DoorDash - Bluestone Lane'
        return 'DoorDash'
    if 'TORY BURCH' in d: return 'Tory Burch'
    if 'MUNA' in d: return 'Muna Wellness'
    if 'EDIKTED' in d: return 'Edikted Fashion'
    if 'ALO' in d: return 'Alo Yoga'
    if 'BLUE BOTTLE' in d: return 'Blue Bottle Coffee'
    if 'DUANE READE' in d: return 'Duane Reade'
    if 'TARGET' in d: return 'Target'
    if 'AUDIBLE' in d: return 'Audible'
    if 'VICTORY BOXING' in d: return 'Victory Boxing Club'
    if 'NETFLIX' in d: return 'Netflix'
    if 'MIDJOURNEY' in d: return 'Midjourney AI'
    if 'YOUTUBE' in d: return 'YouTube Premium'
    if 'ARITZIA' in d: return 'Aritzia'
    if 'CHANEL' in d: return 'Chanel'
    if 'ALICE AND OLIVIA' in d or 'ALICE' in d: return 'Alice + Olivia'
    if 'JIMMY FAIRLY' in d: return 'Jimmy Fairly'
    if 'NYCT PAYGO' in d or 'MTA' in d: return 'MTA NYC Transit'
    if 'TMOBILE' in d or 'T-MOBILE' in d: return 'T-Mobile'
    if 'MICROSOFT' in d: return 'Microsoft'
    if 'NIKE' in d: return 'Nike'
    if 'MANGO' in d: return 'Mango'
    if 'SMCP' in d: return 'Sandro / Maje (SMCP)'
    if 'LIONESS' in d: return 'Lioness Fashion'
    if 'FOR LOVE AND LEM' in d or 'LOVE AND LEMONS' in d: return 'For Love & Lemons'
    if 'PLAYSTATION' in d: return 'PlayStation Store'
    if 'BG ONLINE' in d: return 'Bergdorf Goodman'
    if 'MERCADOPAGO' in d or 'MERCADO PAGO' in d: return 'Mercado Pago'
    if 'TRIMBLE' in d: return 'Trimble Inc'
    if 'CVSExtraCare' in d or 'CVS' in d: return 'CVS Pharmacy'
    if 'WHOOP' in d: return 'Whoop'
    
    # Strip statement noise prefixes
    cleaned = re.sub(r'^(AplPay|GglPay|TST\*|SP\*|BT\*|DD \*|SQ \*|PAYPAL \*)\s*', '', d, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+(NEW YORK|MANHATTAN|BEVERLY HILLS|LOS ANGELES|SAN FRANCISCO|BROOKLYN|DORAL|HICKSVILLE|WESTBURY)\b.*', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip() or d

def categorize(merchant: str, orig_cat: str, amt: float):
    m = (str(merchant) + " " + str(orig_cat)).lower()
    
    if amt < 0:
        return "Refunds & Credits", "Refund", "Refunds & Credits", ["#Refund", "#Credit"], 5

    # 1. Shopping (Monarch Category: Shopping)
    if any(k in m for k in ['nordstrom', 'sephora', 'skims', 'bala', 'bloomingdales', 'tory burch', 'edikted', 'alo', 'aritzia', 'chanel', 'alice', 'jimmy fairly', 'nike', 'bergdorf', 'macy', 'saks', 'mango', 'smcp', 'lioness', 'love and lem', 'cakes body', 'somewherenowhere', 'hair bar', 'apparel', 'clothing', 'shoes', 'boutique', 'target', 'amazon', 'retail', 'store']):
        is_luxury = any(k in m for k in ['nordstrom', 'sephora', 'skims', 'bala', 'bloomingdales', 'tory burch', 'edikted', 'alo', 'aritzia', 'chanel', 'alice', 'jimmy fairly', 'nike', 'bergdorf', 'macy', 'saks', 'mango', 'smcp', 'lioness', 'love and lem'])
        subcat = "Clothing & Luxury" if is_luxury else "General Shopping"
        return "Shopping", subcat, "Shopping", ["#Shopping", "#Clothing" if is_luxury else "#Retail"], 1 if is_luxury else 3

    # 2. Food & Dining (Monarch Category: Food & Dining)
    if any(k in m for k in ['grubhub', 'doordash', 'rappi', 'blue bottle', 'maman', 'bluestone', 'white maize', 'daily pr', 'pepegiallo', 'makiamano', 'cafe sirena', 'birri', 'tacos', 'suram', 'a-ok cafe', 'sui yoga & cafe', 'whole foods', 'wholefds', 'grocery', 'fresh', 'trader joe', 'supermarket', 'market', 'restaurant', 'bakery', 'coffee', 'diner', 'pizza', 'burger', 'bar', 'kitchen', 'cafe']):
        is_grocery = any(k in m for k in ['whole foods', 'wholefds', 'grocery', 'fresh', 'trader joe', 'supermarket', 'market'])
        is_dining = any(k in m for k in ['tacos', 'suram', 'a-ok cafe', 'sui yoga & cafe', 'pepegiallo', 'maman', 'bluestone', 'white maize', 'restaurant', 'bakery', 'coffee', 'cafe', 'bar'])
        subcat = "Groceries" if is_grocery else "Restaurants & Bars" if is_dining else "Food Delivery"
        return "Food & Dining", subcat, "Food & Dining", ["#Food", "#Groceries" if is_grocery else "#Dining"], 4 if is_grocery else 2

    # 3. Travel & Transportation (Monarch Category: Travel & Lifestyle / Transportation)
    if any(k in m for k in ['delta', 'uber', 'lyft', 'mta', 'transit', 'airline', 'flight', 'hotel', 'edreams', 'travix', 'hudson river', 'parking', 'taxi', 'travel']):
        is_flight = any(k in m for k in ['delta', 'flight', 'airline', 'edreams', 'travix'])
        subcat = "Air Travel & Flights" if is_flight else "Rideshare & Transit"
        return "Travel & Transportation", subcat, "Travel & Transportation", ["#Travel", "#Flights" if is_flight else "#Transit"], 3

    # 4. Medical & Healthcare (Monarch Category: Medical & Healthcare)
    if any(k in m for k in ['sisu clinic', 'nyu langone', 'summit medical', 'muna wellness', 'barbershop', 'equinox', 'fitness', 'doctor', 'clinic', 'dental', 'medical', 'pharmacy', 'duane reade', 'cvs', 'walgreens', 'questhealth', 'farmacia', 'health', 'wellness']):
        is_clinic = any(k in m for k in ['sisu clinic', 'nyu langone', 'summit medical', 'clinic', 'dental', 'medical', 'questhealth'])
        is_pharmacy = any(k in m for k in ['duane reade', 'cvs', 'walgreens', 'pharmacy', 'farmacia'])
        subcat = "Doctor & Clinic Visits" if is_clinic else "Pharmacy" if is_pharmacy else "Fitness & Wellness"
        return "Medical & Healthcare", subcat, "Medical & Healthcare", ["#Healthcare", "#Medical" if is_clinic else "#Wellness"], 4

    # 5. Housing & Utilities (Monarch Category: Housing & Utilities)
    if any(k in m for k in ['mattress firm', 'container', 'muji', 'furniture', 'home goods', 'just energy', 'hercules', 'electric', 'utility', 'coned', 'cleaners', 'laundry', 'storage', 'gas', 'water', 'rent', 'mortgage']):
        is_util = any(k in m for k in ['just energy', 'electric', 'utility', 'coned', 'gas', 'water'])
        subcat = "Utilities & Power" if is_util else "Home Improvement & Decor"
        return "Housing & Utilities", subcat, "Housing & Utilities", ["#Housing", "#Utilities" if is_util else "#HomeDecor"], 4

    # 6. Subscriptions & Tech (Monarch Category: Subscriptions & Tech)
    if any(k in m for k in ['netflix', 'midjourney', 'audible', 'kindle', 'prime video', 'playstation', 't-mobile', 'microsoft', 'trimble', 'spotify', 'apple', 'youtube', 'google*boldvoi', 'iq_impuls', 'whoop', 'software', 'cloud', 'subscription']):
        is_mobile = 't-mobile' in m or 'tmobile' in m
        is_media = any(k in m for k in ['netflix', 'youtube', 'spotify', 'audible', 'kindle', 'prime video'])
        subcat = "Mobile & Internet" if is_mobile else "Streaming & Media" if is_media else "Software & Cloud Services"
        return "Subscriptions & Tech", subcat, "Subscriptions & Tech", ["#Subscriptions", "#Software"], 3

    # 7. Entertainment & Recreation (Monarch Category: Entertainment & Recreation)
    if any(k in m for k in ['dice.fm', 'cinema', 'thecinemas', 'ticket', 'theater', 'concert', 'club', 'event']):
        return "Entertainment & Recreation", "Events & Shows", "Entertainment & Recreation", ["#Entertainment", "#Events"], 2

    # 8. Financial & Operations
    return "Financial & Operations", "General Services", "Financial & Operations", ["#Financial", "#Operations"], 3

def get_member_initials(member_name: str) -> str:
    parts = str(member_name).strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1 and len(parts[0]) > 0:
        return parts[0][:2].upper()
    return "HM"

TAXONOMY_CACHE_PATH = "/Users/jesusarguelles/.gemini/jetski/brain/bcc57a77-5608-4a79-bef0-a6bce4cafa40/scratch/grounded_merchant_taxonomy.json"

def _get_grounded_taxonomy() -> Dict[str, Any]:
    if os.path.exists(TAXONOMY_CACHE_PATH):
        try:
            with open(TAXONOMY_CACHE_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def process_csv_dataframe(df: pd.DataFrame, output_json_path: str) -> List[Dict[str, Any]]:
    """Process, deduplicate, enrich, and cross-match returns across single or multiple statement DataFrames."""
    dedup_cols = [c for c in ['Date', 'Card Member', 'Amount', 'Description'] if c in df.columns]
    if dedup_cols:
        df = df.drop_duplicates(subset=dedup_cols).reset_index(drop=True)

    taxonomy = _get_grounded_taxonomy()
    enriched_records = []
    
    for idx, row in df.iterrows():
        try:
            amt = float(str(row['Amount']).replace('$', '').replace(',', ''))
        except (ValueError, TypeError):
            amt = 0.0
            
        desc = str(row.get('Description', ''))
        base_clean = clean_merchant_name(desc)
        
        # Check Google Search grounded taxonomy
        lookup_key = desc.strip() if '*' in desc or len(base_clean) > 25 else base_clean.strip()
        tax_entry = taxonomy.get(lookup_key) or taxonomy.get(base_clean.strip()) or taxonomy.get(desc.strip())
        
        if tax_entry:
            clean_m = tax_entry.get('clean_merchant', base_clean)
            cluster_sub = tax_entry.get('cluster_subcategory')
            cluster_grp = tax_entry.get('cluster_group')
            brand_tags = tax_entry.get('brand_keywords', [])
        else:
            clean_m = base_clean
            cluster_sub = None
            cluster_grp = None
            brand_tags = []

        cat, subcat, exp_type, tags, necessity = categorize(clean_m, row.get('Category', ''), amt)
        card_member = str(row.get('Card Member', 'CARDHOLDER')).strip()
        
        # Merge brand tags if present
        all_tags = list(dict.fromkeys(tags + [f"#{t.replace(' ', '')}" for t in brand_tags]))
        
        record = {
            'id': f"tx_{idx+1}",
            'date': str(row.get('Date', '')),
            'card_member': card_member,
            'card_member_initials': get_member_initials(card_member),
            'account_num': str(row.get('Account #', '')),
            'raw_description': desc,
            'clean_merchant': clean_m,
            'amount': round(amt, 2),
            'is_refund': amt < 0 or 'REFUND' in desc.upper() or 'CREDIT' in desc.upper(),
            'has_return': False,
            'return_amount': 0.0,
            'return_date': None,
            'is_fully_returned': False,
            'net_amount': round(amt, 2) if amt > 0 else 0.0,
            'matched_purchase_id': None,
            'original_category': str(row.get('Category', '')),
            'primary_category': cat,
            'subcategory': subcat,
            'cluster_subcategory': cluster_sub or subcat,
            'cluster_group': cluster_grp or cat,
            'brand_keywords': brand_tags,
            'expense_type': exp_type,
            'tags': all_tags,
            'necessity_score': necessity,
            'extended_details': str(row.get('Extended Details', '')) if pd.notnull(row.get('Extended Details')) else '',
            'city_state': str(row.get('City/State', '')) if pd.notnull(row.get('City/State')) else '',
            'country': str(row.get('Country', 'UNITED STATES')) if pd.notnull(row.get('Country')) else 'UNITED STATES'
        }
        enriched_records.append(record)

    # Cross-Statement Return & Refund Matching Algorithm
    refunds = [r for r in enriched_records if r['amount'] < 0]
    purchases = [r for r in enriched_records if r['amount'] > 0]

    for ref in refunds:
        ref_amt = abs(ref['amount'])
        ref_merchant = ref['clean_merchant'].lower()
        ref_member = ref['card_member'].lower()
        
        best_match = None
        for p in purchases:
            if p['clean_merchant'].lower() == ref_merchant and p['card_member'].lower() == ref_member and not p['is_fully_returned']:
                if abs(p['amount'] - ref_amt) < 0.01:
                    best_match = p
                    break
                elif p['amount'] >= ref_amt and best_match is None:
                    best_match = p
        
        if best_match:
            best_match['has_return'] = True
            best_match['return_amount'] = round(best_match['return_amount'] + ref_amt, 2)
            best_match['return_date'] = ref['date']
            best_match['net_amount'] = max(0.0, round(best_match['amount'] - best_match['return_amount'], 2))
            if best_match['net_amount'] == 0.0:
                best_match['is_fully_returned'] = True
            ref['matched_purchase_id'] = best_match['id']

    # Ensure output directory exists and save enriched JSON
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w') as f:
        json.dump(enriched_records, f, indent=2)

    return enriched_records
