import json
import pandas as pd
import os
from typing import List, Dict, Any

def clean_merchant_name(desc: str) -> str:
    d = str(desc).strip()
    if 'DELTA AIR LINES' in d: return 'Delta Air Lines'
    if 'NORDSTROM' in d: return 'Nordstrom Direct'
    if 'SEPHORA' in d: return 'Sephora'
    if 'NYU LANGONE' in d: return 'NYU Langone Medical'
    if 'AMAZON' in d or 'AMZN' in d or 'KINDLE' in d or 'PRIME VIDEO' in d:
        if 'TIPS' in d: return 'Amazon Tips'
        if 'GROCERY' in d: return 'Amazon Fresh / Grocery'
        if 'KINDLE' in d: return 'Amazon Kindle'
        if 'PRIME' in d: return 'Prime Video'
        return 'Amazon'
    if 'SKIMS' in d: return 'SKIMS'
    if 'SHOPBALA' in d: return 'Bala Bangles'
    if 'UBER' in d: return 'Uber / Uber Eats'
    if 'RAPPI' in d: return 'Rappi'
    if 'BLOOMINGDALES' in d: return 'Bloomingdales'
    if 'GRUBHUB' in d:
        if 'MAMAN' in d: return 'Grubhub - Maman'
        if 'BLUES' in d or 'BLUESTONE' in d: return 'Grubhub - Bluestone Lane'
        if 'WHITE' in d: return 'Grubhub - White Maize'
        if 'GHPLUS' in d: return 'Grubhub Plus'
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
    if 'DUANE READE' in d: return 'Duane Reade / Walgreens'
    if 'TARGET' in d: return 'Target'
    if 'AUDIBLE' in d: return 'Audible'
    if 'VICTORY BOXING' in d: return 'Victory Boxing Club'
    if 'NETFLIX' in d: return 'Netflix'
    if 'MIDJOURNEY' in d: return 'Midjourney AI'
    if 'ARITZIA' in d: return 'Aritzia'
    if 'CHANEL' in d: return 'Chanel'
    if 'ALICE AND OLIVIA' in d: return 'Alice + Olivia'
    if 'JIMMY FAIRLY' in d: return 'Jimmy Fairly'
    if 'NYCT PAYGO' in d: return 'MTA NYC Transit'
    if 'TMOBILE' in d: return 'T-Mobile'
    if 'MICROSOFT' in d: return 'Microsoft'
    if 'NIKE' in d: return 'Nike'
    if 'PLAYSTATION' in d: return 'PlayStation Store'
    if 'BG ONLINE' in d: return 'Bergdorf Goodman'
    if 'MERCADOPAGO' in d: return 'Mercado Pago'
    if 'TRIMBLE' in d: return 'Trimble Inc'
    if 'CVSExtraCare' in d: return 'CVS Pharmacy'
    return d

def categorize(merchant: str, orig_cat: str, amt: float):
    m = merchant.lower()
    c = str(orig_cat).lower()
    
    if amt < 0:
        return "Refund & Credit", "Refund", "Refund/Credit", ["#Refund", "#Credit"], 5

    if any(k in m for k in ['grubhub', 'doordash', 'rappi', 'blue bottle', 'maman', 'bluestone', 'white maize', 'daily pr', 'pepegiallo', 'makiamano', 'cafe sirena', 'birri']):
        return "Dining & Food Delivery", "Food Delivery", "Food & Dining", ["#DeliveryApp", "#Dining"], 2

    if any(k in m for k in ['whole foods', 'grocery', 'duane reade', 'target', 'cvs', 'hercules']):
        return "Groceries & Household", "Supermarket", "Essential", ["#Groceries", "#Household"], 4

    if any(k in m for k in ['nordstrom', 'sephora', 'skims', 'bala', 'bloomingdales', 'tory burch', 'edikted', 'alo', 'aritzia', 'chanel', 'alice', 'jimmy fairly', 'nike', 'bergdorf']):
        return "Fashion, Beauty & Luxury", "Luxury Apparel", "Lifestyle & Luxury", ["#Fashion", "#Beauty", "#Luxury"], 1

    if any(k in m for k in ['delta', 'uber', 'mta', 'hudson river']):
        return "Travel & Transit", "Air Travel" if 'delta' in m else "Transit", "Travel & Transit", ["#Travel", "#Transit"], 3

    if any(k in m for k in ['netflix', 'midjourney', 'audible', 'kindle', 'prime video', 'playstation', 't-mobile', 'microsoft', 'trimble']):
        return "Digital & Subscriptions", "Streaming & Software", "Subscription", ["#Subscription", "#Software"], 3

    if any(k in m for k in ['nyu langone', 'victory boxing', 'muna wellness', 'barbershop']):
        return "Health & Fitness", "Medical & Clinic", "Healthcare", ["#Healthcare", "#Fitness"], 4

    if 'petsmart' in m:
        return "Pet Care", "Pet Supplies", "Pet Care", ["#PetCare", "#Petsmart"], 4

    return "Services & General", "General Services", "Essential", ["#General"], 3

def process_csv_dataframe(df: pd.DataFrame, output_json_path: str) -> List[Dict[str, Any]]:
    enriched_records = []
    for idx, row in df.iterrows():
        try:
            amt = float(str(row['Amount']).replace('$', '').replace(',', ''))
        except (ValueError, TypeError):
            amt = 0.0
            
        desc = str(row.get('Description', ''))
        clean_m = clean_merchant_name(desc)
        cat, subcat, exp_type, tags, necessity = categorize(clean_m, row.get('Category', ''), amt)
        
        record = {
            'id': f"tx_{idx+1}",
            'date': str(row.get('Date', '')),
            'card_member': str(row.get('Card Member', 'CARDHOLDER')),
            'account_num': str(row.get('Account #', '')),
            'raw_description': desc,
            'clean_merchant': clean_m,
            'amount': amt,
            'is_refund': amt < 0,
            'original_category': str(row.get('Category', '')),
            'primary_category': cat,
            'subcategory': subcat,
            'expense_type': exp_type,
            'tags': tags,
            'necessity_score': necessity,
            'extended_details': str(row.get('Extended Details', '')) if pd.notnull(row.get('Extended Details')) else '',
            'city_state': str(row.get('City/State', '')) if pd.notnull(row.get('City/State')) else '',
            'country': str(row.get('Country', 'UNITED STATES')) if pd.notnull(row.get('Country')) else 'UNITED STATES'
        }
        enriched_records.append(record)

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w') as f:
        json.dump(enriched_records, f, indent=2)

    return enriched_records
