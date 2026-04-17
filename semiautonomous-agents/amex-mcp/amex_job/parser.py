"""CSV parser for American Express credit card statements."""

import csv
import io
import json
import logging
import re
from calendar import monthrange
from typing import Optional

logger = logging.getLogger("amex-job.parser")


def _parse_amount(raw: str) -> float:
    """Normalize Amex amount strings to float.

    Handles: $1,234.56  -$1,234.56  (1,234.56)  1234.56  -1234.56
    """
    s = raw.strip()
    if not s or s == "--":
        return 0.0
    negative = False
    if s.startswith("(") and s.endswith(")"):
        negative = True
        s = s[1:-1]
    if s.startswith("-"):
        negative = True
        s = s[1:]
    s = s.replace("$", "").replace(",", "").strip()
    try:
        value = float(s)
    except ValueError:
        logger.warning(json.dumps({"event": "amount_parse_failed", "raw": raw}))
        return 0.0
    return -value if negative else value


def _parse_date(raw: str) -> str:
    """Normalize date strings to YYYY-MM-DD.

    Handles: MM/DD/YYYY  MM/DD/YY
    """
    s = raw.strip()
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", s)
    if not m:
        return s
    month, day, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if year < 100:
        year += 2000
    return f"{year:04d}-{month:02d}-{day:02d}"


def _is_payment(description: str, amount: float) -> bool:
    """Determine if a transaction is a payment/credit."""
    payment_keywords = ["PAYMENT", "THANK YOU", "AUTOPAY", "CREDIT"]
    desc_upper = description.upper()
    return any(kw in desc_upper for kw in payment_keywords) or amount < 0


def _find_header_row(lines: list[str]) -> Optional[int]:
    """Find the CSV header row index by looking for date/description/amount columns."""
    for i, line in enumerate(lines):
        lower = line.lower()
        if "date" in lower and ("description" in lower or "reference" in lower):
            return i
    return None


def parse_statement_csv(csv_content: str, period: str) -> dict:
    """Parse an Amex CSV statement into a structured dict.

    Args:
        csv_content: Raw CSV file content
        period: Statement period as "YYYY-MM"

    Returns:
        Structured statement dict matching Firestore schema
    """
    year, month = int(period[:4]), int(period[5:7])
    _, last_day = monthrange(year, month)

    lines = csv_content.strip().splitlines()
    header_idx = _find_header_row(lines)

    # Extract balance info from metadata lines above header
    balance = 0.0
    minimum_due = 0.0
    due_date = ""
    previous_balance = 0.0

    if header_idx is not None:
        for line in lines[:header_idx]:
            lower = line.lower()
            if "new balance" in lower or "total balance" in lower:
                amounts = re.findall(r'[\$\-\d,]+\.\d{2}', line)
                if amounts:
                    balance = abs(_parse_amount(amounts[-1]))
            elif "minimum" in lower and "due" in lower:
                amounts = re.findall(r'[\$\-\d,]+\.\d{2}', line)
                if amounts:
                    minimum_due = abs(_parse_amount(amounts[-1]))
            elif "due date" in lower or "payment due" in lower:
                dates = re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}', line)
                if dates:
                    due_date = _parse_date(dates[-1])
            elif "previous" in lower and "balance" in lower:
                amounts = re.findall(r'[\$\-\d,]+\.\d{2}', line)
                if amounts:
                    previous_balance = abs(_parse_amount(amounts[-1]))

    # Parse transaction rows
    transactions = []
    payments = []
    total_debits = 0.0
    total_credits = 0.0

    if header_idx is not None:
        data_section = "\n".join(lines[header_idx:])
        reader = csv.DictReader(io.StringIO(data_section))

        # Normalize field names (Amex CSVs vary)
        for row in reader:
            normalized = {k.strip().lower(): v.strip() if v else "" for k, v in row.items() if k}

            # Find the date field
            date_raw = (
                normalized.get("date", "")
                or normalized.get("transaction date", "")
                or normalized.get("date/time", "")
            )
            if not date_raw:
                continue

            date = _parse_date(date_raw)
            post_date = _parse_date(
                normalized.get("post date", "")
                or normalized.get("posted date", "")
                or date_raw
            )
            description = (
                normalized.get("description", "")
                or normalized.get("merchant", "")
                or normalized.get("payee", "")
            )
            amount_raw = (
                normalized.get("amount", "")
                or normalized.get("charge amount", "")
            )
            amount = _parse_amount(amount_raw)
            category = normalized.get("category", "")
            card_member = (
                normalized.get("card member", "")
                or normalized.get("cardholder", "")
                or normalized.get("appears on your statement as", "")
            )

            entry = {
                "date": date,
                "post_date": post_date,
                "description": description,
                "amount": abs(amount),
                "category": category,
                "card_member": card_member,
            }

            if _is_payment(description, amount):
                payments.append({
                    "date": date,
                    "amount": abs(amount),
                    "description": description,
                })
                total_credits += abs(amount)
            else:
                transactions.append(entry)
                total_debits += abs(amount)

    # If we couldn't extract balance from header, compute from transactions
    if balance == 0.0 and (total_debits > 0 or total_credits > 0):
        balance = total_debits - total_credits + previous_balance

    result = {
        "period": period,
        "year": year,
        "month": month,
        "statement_date": f"{year:04d}-{month:02d}-{last_day:02d}",
        "due_date": due_date,
        "balance": round(balance, 2),
        "minimum_due": round(minimum_due, 2),
        "previous_balance": round(previous_balance, 2),
        "payments": payments,
        "transactions": transactions,
        "total_transactions": len(transactions),
        "total_debits": round(total_debits, 2),
        "total_credits": round(total_credits, 2),
        "source": "csv",
    }

    logger.info(json.dumps({
        "event": "csv_parsed",
        "period": period,
        "transactions": len(transactions),
        "payments": len(payments),
    }))

    return result
