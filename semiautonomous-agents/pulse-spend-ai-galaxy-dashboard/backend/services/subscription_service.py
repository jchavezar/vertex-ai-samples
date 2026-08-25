import re
from collections import defaultdict
from typing import List, Dict, Any

KNOWN_SUBSCRIPTIONS = [
    {"pattern": r"NETFLIX", "name": "Netflix", "category": "Streaming & Entertainment", "frequency": "Monthly", "tip": "Review plan tier or consider sharing/annual bundles."},
    {"pattern": r"MIDJOURNEY", "name": "Midjourney AI", "category": "AI & Creative Tools", "frequency": "Monthly", "tip": "Pause or downgrade during low-usage creative cycles."},
    {"pattern": r"AUDIBLE", "name": "Audible", "category": "Audiobooks & Media", "frequency": "Monthly", "tip": "Switch to annual plan or pause credits if unlistened backlog exists."},
    {"pattern": r"PRIME VIDEO|AMZN PRIME", "name": "Amazon Prime / Prime Video", "category": "Streaming & Shopping", "frequency": "Monthly", "tip": "Ensure household members are linked under Amazon Household to avoid duplicate fees."},
    {"pattern": r"KINDLE", "name": "Kindle Unlimited", "category": "E-Books & Reading", "frequency": "Monthly", "tip": "Audit monthly read count to verify active value."},
    {"pattern": r"PLAYSTATION|SONY INTERACTIVE", "name": "PlayStation Plus", "category": "Gaming Subscription", "frequency": "Monthly", "tip": "Switch to 12-month membership for 30%+ savings over monthly billing."},
    {"pattern": r"TMOBILE|T-MOBILE", "name": "T-Mobile Wireless", "category": "Telecom & Mobile", "frequency": "Monthly", "tip": "Audit AutoPay discounts and check for corporate or family plan discounts."},
    {"pattern": r"MICROSOFT", "name": "Microsoft 365", "category": "Productivity & Cloud", "frequency": "Monthly", "tip": "Switch from individual to Family 6-seat plan to share across all devices."},
    {"pattern": r"GHPLUS|GRUBHUB PLUS|GH\*", "name": "Grubhub+ Membership", "category": "Food Delivery Pass", "frequency": "Monthly", "tip": "Check if complimentary membership is included with Amex Gold/Platinum or Amazon Prime."},
    {"pattern": r"DASHPASS|DOORDASH PASS", "name": "DoorDash DashPass", "category": "Food Delivery Pass", "frequency": "Monthly", "tip": "Consolidate to a single delivery subscription to prevent paying dual monthly fees."},
    {"pattern": r"UBER ONE|UBER PASS", "name": "Uber One", "category": "Rides & Delivery", "frequency": "Monthly", "tip": "Check partner credit card statement credits to offset membership costs."},
    {"pattern": r"VICTORY BOXING|EQUINOX|BARRY|SOULCYCLE|PLANET FIT", "name": "Boutique Fitness Membership", "category": "Health & Fitness", "frequency": "Monthly", "tip": "Review attendance per month — consider class packages if attending < 8x/month."},
    {"pattern": r"SPOTIFY", "name": "Spotify Premium", "category": "Music Streaming", "frequency": "Monthly", "tip": "Switch to Duo or Family plan to cut per-person cost in half."},
    {"pattern": r"APPLE\.COM|ICLOUD", "name": "Apple Services / iCloud+", "category": "Cloud & Storage", "frequency": "Monthly", "tip": "Consolidate Apple Music, TV+, and iCloud into Apple One bundle."},
    {"pattern": r"OPENAI|CHATGPT", "name": "ChatGPT Plus", "category": "AI & Productivity", "frequency": "Monthly", "tip": "Audit active team/personal seats."},
    {"pattern": r"TRIMBLE", "name": "Trimble Software", "category": "Professional Software", "frequency": "Monthly", "tip": "Audit annual licensing versus active monthly seat utilization."}
]

def detect_subscriptions(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Detect recurring subscriptions from enriched transaction records."""
    matched_subs = []
    seen_merchants = set()
    
    # 1. Match against known subscription dictionary
    for r in records:
        if r.get('amount', 0) <= 0:
            continue
            
        desc = (r.get('raw_description', '') + " " + r.get('clean_merchant', '')).upper()
        
        for sub_def in KNOWN_SUBSCRIPTIONS:
            if re.search(sub_def['pattern'], desc, re.IGNORECASE):
                key = sub_def['name']
                if key not in seen_merchants:
                    seen_merchants.add(key)
                    amt = abs(r.get('amount', 0))
                    matched_subs.append({
                        "id": f"sub_{len(matched_subs)+1}",
                        "name": sub_def['name'],
                        "clean_merchant": r.get('clean_merchant', sub_def['name']),
                        "category": sub_def['category'],
                        "monthly_amount": round(amt, 2),
                        "annual_projected": round(amt * 12, 2),
                        "billing_frequency": sub_def['frequency'],
                        "card_member": r.get('card_member', 'Household'),
                        "last_billed_date": r.get('date', ''),
                        "status": "Active",
                        "optimization_tip": sub_def['tip'],
                        "is_known_service": True
                    })
                break

    # 2. Heuristic cadence matching for any unclassified recurring amounts
    merchant_groups = defaultdict(list)
    for r in records:
        if r.get('amount', 0) > 0:
            clean = r.get('clean_merchant', '')
            if clean and clean not in seen_merchants:
                merchant_groups[clean].append(r)

    for merchant, txs in merchant_groups.items():
        if len(txs) >= 2:
            amounts = [t['amount'] for t in txs]
            avg_amt = sum(amounts) / len(amounts)
            if all(abs(a - avg_amt) < 1.0 for a in amounts) and avg_amt < 150: # likely recurring utility/service
                matched_subs.append({
                    "id": f"sub_{len(matched_subs)+1}",
                    "name": merchant,
                    "clean_merchant": merchant,
                    "category": txs[0].get('primary_category', 'Recurring Service'),
                    "monthly_amount": round(avg_amt, 2),
                    "annual_projected": round(avg_amt * 12, 2),
                    "billing_frequency": "Monthly",
                    "card_member": txs[0].get('card_member', 'Household'),
                    "last_billed_date": txs[-1].get('date', ''),
                    "status": "Active",
                    "optimization_tip": "Recurring recurring charge detected across statement dates. Verify ongoing necessity.",
                    "is_known_service": False
                })

    # Sort by monthly amount descending
    matched_subs.sort(key=lambda x: x['monthly_amount'], reverse=True)
    
    total_monthly = sum(s['monthly_amount'] for s in matched_subs)
    total_annual = total_monthly * 12

    return {
        "subscription_count": len(matched_subs),
        "total_monthly_recurring": round(total_monthly, 2),
        "total_annual_projected": round(total_annual, 2),
        "potential_annual_savings": round(total_annual * 0.35, 2), # 35% typical subscription optimization
        "subscriptions": matched_subs
    }
