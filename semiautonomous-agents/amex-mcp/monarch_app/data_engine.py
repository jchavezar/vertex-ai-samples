"""Monarch Money / Sovereign Finance Data Engine & Refund Pairing Pipeline.

Pulls all live accounts, statements, outflows, and inflows from Firestore (`vtxdemos`),
normalizes merchants, assigns Monarch categories & Flex Budget buckets, detects
internal transfers vs income vs refunds vs expenses, and pairs merchant returns
against original purchases to compute True Net Spend.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.cloud import firestore

PROJECT_ID = "vtxdemos"
DATA_CACHE_PATH = Path(__file__).parent / "monarch_dataset.json"
USER_OVERRIDES_PATH = Path(__file__).parent / "user_overrides.json"


def load_user_overrides() -> dict[str, dict[str, Any]]:
    if USER_OVERRIDES_PATH.exists():
        try:
            return json.loads(USER_OVERRIDES_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_user_override(txn_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    overrides = load_user_overrides()
    cur = overrides.get(txn_id, {})
    cur.update(patch)
    overrides[txn_id] = cur
    USER_OVERRIDES_PATH.write_text(json.dumps(overrides, indent=2), encoding="utf-8")
    return cur


def clean_merchant_and_classify(desc: str, amount: float, direction: str, institution: str, account_name: str, date_str: str) -> dict[str, Any]:
    """Classify a transaction into Monarch category, group, flex bucket, clean merchant, and tags."""
    u = desc.upper()
    tags: list[str] = []

    # 1. Detect Internal Transfers & Credit Card Payments first
    if direction == "inflow":
        if any(k in u for k in [
            "ONLINE PAYMENT - THANK YOU",
            "PAYMENT FROM CHK",
            "DEPOSIT: FROM SAVINGS",
            "FROM SAVINGS - 2752",
            "SOFI BANK        DES:TRANSFER",
            "RETURN OF POSTED CHECK",
        ]):
            if "2752" in u:
                tags.append("#311-lease-funding")
            return {
                "txn_type": "transfer",
                "merchant_clean": "Internal Account / Card Transfer",
                "category": "Credit Card Payment & Transfers",
                "group": "Transfers",
                "flex_bucket": "Transfer",
                "tags": tags,
            }
        if "GOOGLE LLC" in u:
            tags.append("#payroll")
            return {
                "txn_type": "income",
                "merchant_clean": "Google LLC Payroll",
                "category": "Paychecks & Salary",
                "group": "Income",
                "flex_bucket": "Income",
                "tags": tags,
            }
        if "MORGAN STANLEY" in u:
            tags.extend(["#equity-vest", "#gsu"])
            return {
                "txn_type": "income",
                "merchant_clean": "Morgan Stanley Equity / GSU Release",
                "category": "Equity & Investment Inflows",
                "group": "Income",
                "flex_bucket": "Income",
                "tags": tags,
            }
        if "INTEREST EARNED" in u or "VANGUARD" in u or "6725" in account_name or "BROKERAGE" in account_name.upper():
            tags.append("#passive-income")
            return {
                "txn_type": "income",
                "merchant_clean": "Interest & Dividends (" + institution.upper() + ")",
                "category": "Interest & Dividends",
                "group": "Income",
                "flex_bucket": "Income",
                "tags": tags,
            }
        if "MOBILE" in u and "DEPOSIT" in u:
            return {
                "txn_type": "income",
                "merchant_clean": "BofA Mobile Check Deposit",
                "category": "Other Income & Deposits",
                "group": "Income",
                "flex_bucket": "Income",
                "tags": tags,
            }
        # Otherwise, an inflow on a credit card or checking debit card is a Merchant Refund / Return!
        tags.append("#refund")
        base = _classify_expense_merchant(desc, institution, account_name, date_str)
        return {
            "txn_type": "refund",
            "merchant_clean": base["merchant_clean"],
            "merchant_key": base["merchant_key"],
            "category": base["category"],
            "group": base["group"],
            "flex_bucket": base["flex_bucket"],
            "tags": list(set(tags + base["tags"])),
        }

    # 2. Outflows: Check if it's an internal transfer, credit card bill payment, or refundable security deposit escrow
    if any(k in u for k in [
        "AMERICAN EXPRESS DES:ACH PMT",
        "AMERICAN EXPRESS DES:RETRY PYMT",
        "MOBILE BANKING PAYMENT TO CRD",
        "WITHDRAWAL: TO CHECKING",
        "TO CHECKING - 5857",
        "ACH: BANK OF AMERICA",
        "HENRY HALL - SEC",
    ]):
        if "2752" in account_name or "TO CHECKING - 5857" in u:
            tags.append("#311-lease-funding")
        if "HENRY HALL - SEC" in u:
            tags.append("#security-deposit-escrow")
        return {
            "txn_type": "transfer",
            "merchant_clean": "Henry Hall Security Deposit (Escrow)" if "HENRY HALL - SEC" in u else "Internal Account / Card Payment",
            "merchant_key": "SECURITY_DEPOSIT" if "HENRY HALL - SEC" in u else "INTERNAL_TRANSFER",
            "category": "Security Deposit & Transfers" if "HENRY HALL - SEC" in u else "Credit Card Payment & Transfers",
            "group": "Transfers",
            "flex_bucket": "Transfer",
            "tags": tags,
        }

    # 3. True Expense Classification
    base = _classify_expense_merchant(desc, institution, account_name, date_str)
    return {
        "txn_type": "expense",
        "merchant_clean": base["merchant_clean"],
        "merchant_key": base["merchant_key"],
        "category": base["category"],
        "group": base["group"],
        "flex_bucket": base["flex_bucket"],
        "tags": base["tags"],
    }


def _classify_expense_merchant(desc: str, institution: str, account_name: str, date_str: str) -> dict[str, Any]:
    u = desc.upper()
    tags: list[str] = []

    # Housing & Rent (Fixed) — Distinguish the TWO separate landlords cleanly!
    # 1) HENRY HALL (515 W 38th St Apt 19A — Canvas Property Group / Bilt)
    if "HENRY HALL" in u:
        tags.append("#henry-hall-19a")
        tags.append("#move-in-first-month")
        return {
            "merchant_clean": "Henry Hall (515 W 38th Apt 19A — Move-In Rent)",
            "merchant_key": "HENRY_HALL_RENT",
            "category": "Housing & Rent",
            "group": "Housing & Fixed Bills",
            "flex_bucket": "Fixed",
            "tags": tags,
        }

    if "BILTRENT" in u or "BILT PAYMENT" in u:
        tags.append("#henry-hall-19a")
        tags.append("#primary-residence")
        return {
            "merchant_clean": "Henry Hall via Bilt (515 W 38th Apt 19A)",
            "merchant_key": "HENRY_HALL_RENT",
            "category": "Housing & Rent",
            "group": "Housing & Fixed Bills",
            "flex_bucket": "Fixed",
            "tags": tags,
        }

    # 2) KADIMA TENTH AVE / LALEZARIAN PROPERTIES (507 W 28th St — Unit 822 & Former Unit 7C)
    if "KADIMA TENTH AVE" in u:
        if date_str.startswith("2026-07"):
            tags.append("#507w28-unit-7c")
            return {
                "merchant_clean": "Kadima Tenth Ave (507 W 28th Apt 7C — Ended Aug 31)",
                "merchant_key": "KADIMA_7C_RENT",
                "category": "Housing & Rent",
                "group": "Housing & Fixed Bills",
                "flex_bucket": "Fixed",
                "tags": tags,
            }
        tags.append("#507w28-unit-822")
        return {
            "merchant_clean": "Kadima Tenth Ave (507 W 28th Unit 822)",
            "merchant_key": "KADIMA_822_RENT",
            "category": "Housing & Rent",
            "group": "Housing & Fixed Bills",
            "flex_bucket": "Fixed",
            "tags": tags,
        }

    if "OTTER MOVING" in u:
        tags.append("#move-in")
        return {
            "merchant_clean": "Otter Moving & Storage",
            "merchant_key": "OTTER_MOVING",
            "category": "Housing & Rent",
            "group": "Housing & Fixed Bills",
            "flex_bucket": "Non-Monthly",
            "tags": tags,
        }

    # Utilities & Insurance (Fixed)
    if "CON ED" in u or "CECONY" in u:
        if "102686" in u:
            tags.append("#311-lease")
        return {
            "merchant_clean": "Con Edison of NY",
            "merchant_key": "CON_EDISON",
            "category": "Utilities & Insurance",
            "group": "Housing & Fixed Bills",
            "flex_bucket": "Fixed",
            "tags": tags,
        }
    if "VERIZON" in u:
        tags.append("#recurring")
        return {
            "merchant_clean": "Verizon Wireless / Fios",
            "merchant_key": "VERIZON",
            "category": "Utilities & Insurance",
            "group": "Housing & Fixed Bills",
            "flex_bucket": "Fixed",
            "tags": tags,
        }
    if "JUST ENERGY" in u or "GAS METROPOLITANO" in u or "TELMEX" in u or "DIRECTV" in u:
        tags.append("#recurring")
        return {
            "merchant_clean": "Utilities & Telecom (" + (
                "Just Energy" if "JUST ENERGY" in u else
                "Gas Metropolitano" if "GAS" in u else
                "Telmex" if "TELMEX" in u else "DirecTV"
            ) + ")",
            "merchant_key": "UTILITIES_OTHER",
            "category": "Utilities & Insurance",
            "group": "Housing & Fixed Bills",
            "flex_bucket": "Fixed",
            "tags": tags,
        }
    if "GEICO" in u or "LEMONADE" in u:
        return {
            "merchant_clean": "Geico Auto Insurance" if "GEICO" in u else "Lemonade Insurance",
            "merchant_key": "GEICO" if "GEICO" in u else "LEMONADE",
            "category": "Utilities & Insurance",
            "group": "Housing & Fixed Bills",
            "flex_bucket": "Fixed",
            "tags": tags,
        }

    # Subscriptions & Digital (Fixed)
    if any(k in u for k in ["APPLE.COM", "YOUTUBEPREMIUM", "MICROSOFT", "SCRIBD", "GOOGLE *GOOGLE STORE", "SIMPLEFIN", "DICE.FM", "OPENAI", "ANTHROPIC", "CLAUDE", "CURSOR"]):
        tags.append("#subscription")
        m_name = (
            "Apple Services / iCloud" if "APPLE.COM" in u else
            "YouTube Premium" if "YOUTUBE" in u else
            "Microsoft 365 / Xbox" if "MICROSOFT" in u else
            "Scribd Subscription" if "SCRIBD" in u else
            "Google Store / Google One" if "GOOGLE" in u else
            "SimpleFIN Bridge" if "SIMPLEFIN" in u else
            "Dice.fm Events" if "DICE.FM" in u else desc[:28].title()
        )
        m_key = (
            "APPLE_BILL" if "APPLE.COM" in u else
            "GOOGLE_STORE" if "GOOGLE *GOOGLE STORE" in u else
            m_name.upper().replace(" ", "_")
        )
        return {
            "merchant_clean": m_name,
            "merchant_key": m_key,
            "category": "Subscriptions & Digital",
            "group": "Housing & Fixed Bills",
            "flex_bucket": "Fixed",
            "tags": tags,
        }

    # Apparel & Luxury Shopping (Flexible)
    if any(k in u for k in [
        "ARITZIA", "SP ALO", "ALO YOGA", "SKIMS", "SAKS ", "SEPHORA", "BLOOMINGDALE",
        "ALICE AND OLIVIA", "JIMMY FAIRLY", "BVLGARI", "NIKE.COM", "LULULEMON",
        "EDIKTED", "B.TEMPTD", "NUORI", "MACYS", "NORDSTROM", "UNIQLO", "LEVI'S",
        "THEORY", "ALLSAINTS", "PINEDA COVALIN", "LIVERPOOL", "SEARS", "SANBORNS", "CLETO REYES"
    ]):
        if "BVLGARI" in u:
            tags.append("#travel-tokyo")
        m_name, m_key = (
            ("Aritzia", "ARITZIA") if "ARITZIA" in u else
            ("Alo Yoga", "ALO_YOGA") if ("SP ALO" in u or "ALO YOGA" in u) else
            ("Skims", "SKIMS") if "SKIMS" in u else
            ("Bvlgari Omotesando Tokyo", "BVLGARI") if "BVLGARI" in u else
            ("Saks Fifth Avenue", "SAKS") if "SAKS" in u else
            ("Sephora", "SEPHORA") if "SEPHORA" in u else
            ("Bloomingdale's", "BLOOMINGDALES") if "BLOOMINGDALE" in u else
            ("Alice + Olivia", "ALICE_OLIVIA") if "ALICE AND OLIVIA" in u else
            ("Jimmy Fairly Eyewear", "JIMMY_FAIRLY") if "JIMMY FAIRLY" in u else
            ("Nike", "NIKE") if "NIKE.COM" in u else
            ("Lululemon", "LULULEMON") if "LULULEMON" in u else
            ("Edikted", "EDIKTED") if "EDIKTED" in u else
            ("B.Tempt'd", "BTEMPTD") if "B.TEMPTD" in u else
            ("Nuori Skincare", "NUORI") if "NUORI" in u else
            ("Liverpool Mexico", "LIVERPOOL") if "LIVERPOOL" in u else
            ("Cleto Reyes Boxing", "CLETO_REYES") if "CLETO REYES" in u else
            ("Pineda Covalin", "PINEDA_COVALIN") if "PINEDA COVALIN" in u else
            ("Macy's Herald Square", "MACYS") if "MACYS" in u else
            ("Nordstrom Rack", "NORDSTROM") if "NORDSTROM" in u else
            ("AllSaints", "ALLSAINTS") if "ALLSAINTS" in u else
            ("Theory", "THEORY") if "THEORY" in u else
            ("Levi's", "LEVIS") if "LEVI'S" in u else
            ("Uniqlo", "UNIQLO") if "UNIQLO" in u else
            (desc[:28].title(), "APPAREL_OTHER")
        )
        return {
            "merchant_clean": m_name,
            "merchant_key": m_key,
            "category": "Apparel & Luxury Shopping",
            "group": "Flexible Living",
            "flex_bucket": "Flexible",
            "tags": tags,
        }

    # Travel, Flights & Hotels (Non-Monthly)
    if any(k in u for k in [
        "DELTA AIR", "BOOKING.COM", "TRIVAGO", "EL ARTE GASTRONOMICO", "ENTERPRISE",
        "AVIS RENT", "AMTRAK", "SHIBUYA", "DONQUIJOTE", "FAMILYMART", "TOKYO",
        "HAPPYONE", "LA SOFFITTA", "UTAHIROBA", "DTW CORKTOWN", "AEROMEXICO", "HOTEL"
    ]):
        tags.append("#travel")
        m_name, m_key = (
            ("Delta Air Lines", "DELTA") if "DELTA AIR" in u else
            ("Hotel on Booking.com (Amsterdam)", "BOOKING_AMSTERDAM") if "BOOKING.COM" in u else
            ("Trivago Hotel Deals", "TRIVAGO") if "TRIVAGO" in u else
            ("El Arte Gastronomico (Mexico)", "ARTE_GASTRONOMICO") if "GASTRONOMICO" in u else
            ("Enterprise Rent-A-Car", "ENTERPRISE") if "ENTERPRISE" in u else
            ("Avis Rent-A-Car", "AVIS") if "AVIS" in u else
            ("Amtrak", "AMTRAK") if "AMTRAK" in u else
            ("Tokyo Dining & Retail", "TOKYO_TRAVEL") if any(x in u for x in ["SHIBUYA", "DONQUIJOTE", "FAMILYMART", "TOKYO", "HAPPYONE", "LA SOFFITTA", "UTAHIROBA"]) else
            (desc[:28].title(), "TRAVEL_OTHER")
        )
        return {
            "merchant_clean": m_name,
            "merchant_key": m_key,
            "category": "Travel, Flights & Hotels",
            "group": "Non-Monthly & Sinking",
            "flex_bucket": "Non-Monthly",
            "tags": tags,
        }

    # Medical, Vet & Aesthetics (Non-Monthly)
    if any(k in u for k in [
        "HEART OF CHELSEA", "DAVID SCHICK", "SISU CLINIC", "NYU LANGONE",
        "HAIR BAR NYC", "HONEY NAIL", "BARBERSHOP", "PELUQUERIA", "FARM GUAD", "RYDERS ALLEY"
    ]):
        m_name, m_key = (
            ("Heart of Chelsea Veterinary", "HEART_OF_CHELSEA") if "HEART OF CHELSEA" in u else
            ("Ryders Alley Veterinary", "RYDERS_ALLEY") if "RYDERS ALLEY" in u else
            ("David Schick MD", "DAVID_SCHICK") if "DAVID SCHICK" in u else
            ("Sisu Clinic NYC", "SISU_CLINIC") if "SISU CLINIC" in u else
            ("NYU Langone Health", "NYU_LANGONE") if "NYU LANGONE" in u else
            ("Hair Bar NYC", "HAIR_BAR") if "HAIR BAR" in u else
            ("Honey Nail Salon", "HONEY_NAIL") if "HONEY NAIL" in u else
            (desc[:28].title(), "MEDICAL_OTHER")
        )
        return {
            "merchant_clean": m_name,
            "merchant_key": m_key,
            "category": "Medical, Vet & Aesthetics",
            "group": "Non-Monthly & Sinking",
            "flex_bucket": "Non-Monthly",
            "tags": tags,
        }

    # Electronics, Home & Retail (Non-Monthly)
    if any(k in u for k in [
        "B&H PHOTO", "VIVIDSTORM", "DYSON", "AMAZON", "AMZN.COM", "ELECTRODOMES",
        "BARNES", "NINTENDO", "CALLIXE"
    ]):
        m_name, m_key = (
            ("B&H Photo Video NYC", "BH_PHOTO") if "B&H PHOTO" in u else
            ("PingPong*Vividstorm HK", "VIVIDSTORM") if "VIVIDSTORM" in u else
            ("Dyson Flagship SoHo", "DYSON") if "DYSON" in u else
            ("Amazon Marketplace", "AMAZON") if ("AMAZON" in u or "AMZN" in u) else
            ("Electrodomes Clicom", "ELECTRODOMES") if "ELECTRODOMES" in u else
            ("Nintendo", "NINTENDO") if "NINTENDO" in u else
            ("Barnes & Noble", "BARNES_NOBLE") if "BARNES" in u else
            (desc[:28].title(), "RETAIL_OTHER")
        )
        return {
            "merchant_clean": m_name,
            "merchant_key": m_key,
            "category": "Electronics, Home & Retail",
            "group": "Non-Monthly & Sinking",
            "flex_bucket": "Non-Monthly",
            "tags": tags,
        }

    # Fitness & Wellness (Flexible)
    if any(k in u for k in ["VICTORY BOXING", "SUI YOGA", "PILATES", "GALAXY GYM", "GYM ENTRENAT", "EQUINOX", "SPACE PING PONG"]):
        m_name, m_key = (
            ("Victory Boxing Club NYC", "VICTORY_BOXING") if "VICTORY BOXING" in u else
            ("Sui Yoga NYC", "SUI_YOGA") if "SUI YOGA" in u else
            ("Space Ping Pong NYC", "SPACE_PING_PONG") if "PING PONG" in u else
            (desc[:26].title(), "FITNESS_OTHER")
        )
        return {
            "merchant_clean": m_name,
            "merchant_key": m_key,
            "category": "Fitness & Wellness",
            "group": "Flexible Living",
            "flex_bucket": "Flexible",
            "tags": tags,
        }

    # Rideshare & Transit (Flexible)
    if any(k in u for k in ["UBER", "LYFT", "NYCT PAYGO", "MTA*", "E-ZPASS", "WAYMO", "CURB"]):
        m_name, m_key = (
            ("Uber Rides", "UBER") if "UBER" in u else
            ("Lyft Rides", "LYFT") if "LYFT" in u else
            ("MTA NYCT Paygo", "MTA_NYCT") if ("NYCT" in u or "MTA" in u) else
            ("E-ZPass NY", "EZPASS") if "E-ZPASS" in u else
            (desc[:26].title(), "TRANSIT_OTHER")
        )
        return {
            "merchant_clean": m_name,
            "merchant_key": m_key,
            "category": "Rideshare & Transit",
            "group": "Flexible Living",
            "flex_bucket": "Flexible",
            "tags": tags,
        }

    # Groceries & Meal Prep (Flexible)
    if any(k in u for k in ["WHOLE FOODS", "NUTRITION SOLUTIONS", "DUANE READE", "PRESTIGE MARKETPLACE", "FOOD MARKET", "CHEDRAUI", "SAMS ", "OXXO", "CVS", "WALGREENS"]):
        m_name, m_key = (
            ("Whole Foods Market", "WHOLE_FOODS") if "WHOLE FOODS" in u else
            ("Nutrition Solutions", "NUTRITION_SOLUTIONS") if "NUTRITION SOLUTIONS" in u else
            ("Duane Reade Pharmacy", "DUANE_READE") if "DUANE READE" in u else
            (desc[:26].title(), "GROCERY_OTHER")
        )
        return {
            "merchant_clean": m_name,
            "merchant_key": m_key,
            "category": "Groceries & Daily Essentials",
            "group": "Flexible Living",
            "flex_bucket": "Flexible",
            "tags": tags,
        }

    # Family Support, Zelle & Cash (Non-Monthly)
    if any(k in u for k in ["WIRE TYPE:FX OUT", "ZELLE PAYMENT", "BKOFAMERICA ATM", "VENMO", "CASH EQUIVALENT", "INTEREST CHARGED"]):
        m_name, m_key = (
            ("International FX Wire (Family Support Mexico)", "FX_WIRE_MEXICO") if "WIRE TYPE:FX" in u else
            ("Zelle Transfer", "ZELLE") if "ZELLE" in u else
            ("BofA ATM Cash Withdrawal", "BOFA_ATM") if "ATM" in u else
            ("Venmo Transfer", "VENMO") if "VENMO" in u else
            (desc[:28].title(), "CASH_OTHER")
        )
        return {
            "merchant_clean": m_name,
            "merchant_key": m_key,
            "category": "Family Support, Zelle & Cash",
            "group": "Non-Monthly & Sinking",
            "flex_bucket": "Non-Monthly",
            "tags": tags,
        }

    # Food Delivery & Dining (Flexible — Default for Grubhub, restaurants, bars, cafes)
    m_name, m_key = (
        ("Grubhub Food Delivery", "GRUBHUB") if "GRUBHUB" in u else
        ("Monarch Rooftop NYC", "MONARCH_ROOFTOP") if "MONARCH ROOFTOP" in u else
        ("Los Tacos No. 1", "LOS_TACOS") if "LOS TACOS" in u else
        ("Jongro Gopchang NYC", "JONGRO") if "JONGRO" in u else
        ("RCI NYC Bar & Grill", "RCI_BAR") if "RCI NYC" in u else
        ("White Maize Chelsea", "WHITE_MAIZE") if "WHITE MAIZE" in u else
        (re.sub(r"\s+", " ", desc)[:30].title(), "DINING_OTHER")
    )
    return {
        "merchant_clean": m_name,
        "merchant_key": m_key,
        "category": "Food Delivery & Dining",
        "group": "Flexible Living",
        "flex_bucket": "Flexible",
        "tags": tags,
    }


def build_monarch_dataset(periods: list[str] | None = None) -> dict[str, Any]:
    """Fetch Firestore data, run classification & refund-pairing engine, and return complete state."""
    db = firestore.Client(project=PROJECT_ID)
    if periods is None:
        periods = ["2026-07", "2026-08", "2026-09", "2026-10"]

    raw_accounts = [d.to_dict() for d in db.collection("bank_accounts").stream()]
    overrides = load_user_overrides()

    # Format accounts with Monarch metadata
    accounts = []
    total_assets = 0.0
    total_liabilities = 0.0
    for acc in raw_accounts:
        bal = float(acc.get("balance", 0.0))
        name = acc.get("name", "")
        inst = acc.get("institution", "unknown")
        is_liability = bal < 0 or "Card" in name or "Signature" in name
        abs_bal = round(abs(bal), 2)
        if is_liability:
            total_liabilities += abs_bal
            acc_type = "Credit Card"
        else:
            total_assets += abs_bal
            if "Brokerage" in name:
                acc_type = "Investment / Brokerage"
            elif "Savings" in name:
                acc_type = "High-Yield Savings"
            else:
                acc_type = "Checking"

        accounts.append({
            "account_id": acc.get("account_id", ""),
            "name": name,
            "institution": inst,
            "institution_label": (
                "American Express" if inst == "amex" else
                "Bank of America" if inst == "bofa" else
                "SoFi" if inst == "sofi" else inst.upper()
            ),
            "type": acc_type,
            "is_liability": is_liability,
            "balance": round(bal, 2),
            "abs_balance": abs_bal,
            "available_balance": round(float(acc.get("available_balance", 0.0)), 2),
            "balance_date": acc.get("balance_date", "2026-10-12"),
            "updated_at": acc.get("updated_at", ""),
        })

    accounts.sort(key=lambda a: (a["is_liability"], a["institution"], -a["abs_balance"]))

    # Load all transactions & inflows across periods
    all_items: list[dict[str, Any]] = []
    for p in sorted(periods):
        doc = db.collection("amex_statements").document(p).get()
        if not doc.exists:
            continue
        s = doc.to_dict()
        for t in s.get("transactions", []):
            txn_id = str(t.get("txn_id") or f"{p}_out_{len(all_items)}")
            desc = t.get("description", "")
            amt = round(float(t.get("amount", 0.0)), 2)
            inst = t.get("institution", "amex").lower()
            acc_name = t.get("account_name", "")
            date_str = t.get("date", "")
            cls = clean_merchant_and_classify(desc, amt, "outflow", inst, acc_name, date_str)
            item = {
                "txn_id": txn_id,
                "date": date_str,
                "period": p,
                "description": desc,
                "merchant_clean": cls["merchant_clean"],
                "merchant_key": cls.get("merchant_key", "OTHER"),
                "category": cls["category"],
                "group": cls["group"],
                "flex_bucket": cls["flex_bucket"],
                "txn_type": cls["txn_type"],  # expense or transfer
                "direction": "outflow",
                "institution": inst,
                "account_name": acc_name,
                "amount": amt,
                "signed_amount": -amt,
                "net_amount": amt if cls["txn_type"] == "expense" else 0.0,
                "refunded_amount": 0.0,
                "refund_status": "none",
                "matched_refunds": [],
                "tags": cls["tags"],
                "needs_review": amt >= 500.0 and cls["txn_type"] == "expense",
                "reviewed": False,
                "notes": "",
            }
            if txn_id in overrides:
                ov = overrides[txn_id]
                for k in ("category", "merchant_clean", "tags", "needs_review", "reviewed", "notes", "flex_bucket"):
                    if k in ov:
                        item[k] = ov[k]
            all_items.append(item)

        for pm in s.get("payments", []):
            txn_id = str(pm.get("txn_id") or f"{p}_in_{len(all_items)}")
            desc = pm.get("description", "")
            amt = round(float(pm.get("amount", 0.0)), 2)
            inst = pm.get("institution", "amex").lower()
            acc_name = pm.get("account_name", "")
            date_str = pm.get("date", "")
            cls = clean_merchant_and_classify(desc, amt, "inflow", inst, acc_name, date_str)
            item = {
                "txn_id": txn_id,
                "date": date_str,
                "period": p,
                "description": desc,
                "merchant_clean": cls["merchant_clean"],
                "merchant_key": cls.get("merchant_key", "OTHER"),
                "category": cls["category"],
                "group": cls["group"],
                "flex_bucket": cls["flex_bucket"],
                "txn_type": cls["txn_type"],  # income, refund, or transfer
                "direction": "inflow",
                "institution": inst,
                "account_name": acc_name,
                "amount": amt,
                "signed_amount": amt,
                "net_amount": 0.0,
                "refunded_amount": 0.0,
                "refund_status": "refund_credit" if cls["txn_type"] == "refund" else "none",
                "matched_refunds": [],
                "tags": cls["tags"],
                "needs_review": False,
                "reviewed": True,
                "notes": "",
            }
            if txn_id in overrides:
                ov = overrides[txn_id]
                for k in ("category", "merchant_clean", "tags", "needs_review", "reviewed", "notes", "flex_bucket"):
                    if k in ov:
                        item[k] = ov[k]
            all_items.append(item)

    # -------------------------------------------------------------------------
    # Refund & Return Pairing Engine (Matches merchant returns to purchases)
    # -------------------------------------------------------------------------
    expenses_by_mkey: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for it in all_items:
        if it["txn_type"] == "expense":
            expenses_by_mkey[it["merchant_key"]].append(it)

    # Sort expenses oldest first or exact-amount match first
    refund_items = [it for it in all_items if it["txn_type"] == "refund"]
    paired_audit_log = []

    for ref in sorted(refund_items, key=lambda x: x["date"]):
        mkey = ref["merchant_key"]
        rem_ref = ref["amount"]
        candidates = expenses_by_mkey.get(mkey, [])

        # Pass 1: Look for exact amount match with remaining net_amount == rem_ref
        exact_match = None
        for exp in candidates:
            if abs(exp["net_amount"] - rem_ref) < 0.02:
                exact_match = exp
                break

        if exact_match is not None:
            exact_match["refunded_amount"] = round(exact_match["refunded_amount"] + rem_ref, 2)
            exact_match["net_amount"] = 0.0
            exact_match["refund_status"] = "full_refund"
            exact_match["matched_refunds"].append({
                "refund_txn_id": ref["txn_id"],
                "date": ref["date"],
                "amount": rem_ref,
            })
            ref["notes"] = f"Matched 100% to {exact_match['date']} charge (${exact_match['amount']:.2f})"
            paired_audit_log.append({
                "refund_date": ref["date"],
                "purchase_date": exact_match["date"],
                "merchant": exact_match["merchant_clean"],
                "institution": exact_match["institution"],
                "original_amount": exact_match["amount"],
                "refund_amount": rem_ref,
                "net_kept": 0.0,
                "status": "100% REFUNDED & REMOVED",
            })
            continue

        # Pass 2: Deduct across largest/closest purchases for that same merchant
        # Sort candidates by date desc (prioritizing Aug/Sep purchases) and largest net_amount
        for exp in sorted(candidates, key=lambda e: (e["date"] <= ref["date"], e["net_amount"]), reverse=True):
            if rem_ref <= 0.005 or exp["net_amount"] <= 0.005:
                continue
            deduct = round(min(exp["net_amount"], rem_ref), 2)
            exp["refunded_amount"] = round(exp["refunded_amount"] + deduct, 2)
            exp["net_amount"] = round(exp["net_amount"] - deduct, 2)
            exp["refund_status"] = "full_refund" if exp["net_amount"] < 0.01 else "partial_refund"
            exp["matched_refunds"].append({
                "refund_txn_id": ref["txn_id"],
                "date": ref["date"],
                "amount": deduct,
            })
            rem_ref = round(rem_ref - deduct, 2)
            paired_audit_log.append({
                "refund_date": ref["date"],
                "purchase_date": exp["date"],
                "merchant": exp["merchant_clean"],
                "institution": exp["institution"],
                "original_amount": exp["amount"],
                "refund_amount": deduct,
                "net_kept": exp["net_amount"],
                "status": "100% REFUNDED & REMOVED" if exp["net_amount"] < 0.01 else f"PARTIAL REFUND (NET ${exp['net_amount']:.2f})",
            })

    all_items.sort(key=lambda x: (x["date"], x["amount"]), reverse=True)

    net_worth = round(total_assets - total_liabilities, 2)
    sofi_2752_bal = next((a["balance"] for a in accounts if "2752" in a["name"]), 26003.87)
    lease_311_remaining = round(3 * 4581.57, 2)  # Nov, Dec, Jan ($13,744.71)
    sofi_2752_unencumbered = round(sofi_2752_bal - lease_311_remaining, 2)

    dataset = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner": "Jesus Chavez (jesusarguelles@google.com / jchavezar@gmail.com)",
        "summary": {
            "total_assets": round(total_assets, 2),
            "total_liabilities": round(total_liabilities, 2),
            "net_worth": net_worth,
            "unencumbered_net_worth": round(net_worth - lease_311_remaining, 2),
            "sofi_2752_balance": sofi_2752_bal,
            "lease_311_remaining_obligation": lease_311_remaining,
            "sofi_2752_true_buffer": sofi_2752_unencumbered,
            "total_records": len(all_items),
            "total_refunds_paired": round(sum(r["amount"] for r in refund_items), 2),
            "refund_count": len(refund_items),
        },
        "accounts": accounts,
        "transactions": all_items,
        "refund_audit_log": paired_audit_log,
    }

    DATA_CACHE_PATH.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
    return dataset


if __name__ == "__main__":
    ds = build_monarch_dataset()
    print("Built dataset:", json.dumps(ds["summary"], indent=2))
