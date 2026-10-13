"""SimpleFIN Bridge client for multi-bank (Amex, Bank of America, SoFi) ingestion."""

import base64
import json
import logging
import os
import urllib.parse
import urllib.request
from calendar import monthrange
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from amex_job.storage import _get_db, get_statement, write_statement

logger = logging.getLogger("amex-job.simplefin")

SECRET_FILE = Path.home() / ".gemini" / "jetski" / ".simplefin_access_url"
ACCOUNTS_COLLECTION = os.environ.get("FIRESTORE_ACCOUNTS_COLLECTION", "bank_accounts")


def save_access_url(access_url: str) -> None:
    """Persist the claimed SimpleFIN Access URL locally with 0600 permissions and in Firestore."""
    SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
    SECRET_FILE.write_text(access_url.strip(), encoding="utf-8")
    os.chmod(SECRET_FILE, 0o600)
    try:
        db = _get_db()
        db.collection("finance_config").document("simplefin").set(
            {
                "access_url": access_url.strip(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    except Exception as e:
        logger.warning(json.dumps({"event": "firestore_token_save_skipped", "error": str(e)}))


def load_access_url() -> Optional[str]:
    """Load the SimpleFIN Access URL from env, local 0600 file, or Firestore."""
    env_url = os.environ.get("SIMPLEFIN_ACCESS_URL", "").strip()
    if env_url:
        return env_url
    if SECRET_FILE.exists():
        val = SECRET_FILE.read_text(encoding="utf-8").strip()
        if val:
            return val
    try:
        db = _get_db()
        doc = db.collection("finance_config").document("simplefin").get()
        if doc.exists:
            return doc.to_dict().get("access_url")
    except Exception:
        pass
    return None


def claim_setup_token(setup_token: str) -> str:
    """Exchange a one-time Base64 SimpleFIN Setup Token for a permanent Access URL."""
    token_clean = setup_token.strip()
    if token_clean.startswith("http://") or token_clean.startswith("https://"):
        # Already an access URL
        save_access_url(token_clean)
        return token_clean

    claim_url = base64.b64decode(token_clean).decode("utf-8").strip()
    req = urllib.request.Request(
        claim_url,
        data=b"",
        headers={"Content-Length": "0", "User-Agent": "jetski-finance-mcp/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        access_url = resp.read().decode("utf-8").strip()

    if not access_url.startswith("http"):
        raise ValueError(f"Unexpected SimpleFIN claim response: {access_url[:100]}")

    save_access_url(access_url)
    return access_url


def _normalize_institution(org_name: str, org_domain: str = "") -> str:
    """Normalize institution name into a clean slug (amex, bofa, sofi, etc.)."""
    combined = f"{org_name} {org_domain}".lower()
    if "american express" in combined or "amex" in combined or "aexp" in combined:
        return "amex"
    if "bank of america" in combined or "bofa" in combined:
        return "bofa"
    if "sofi" in combined:
        return "sofi"
    return org_name.strip() or "unknown"


def fetch_simplefin_data(
    days: int = 60,
    balances_only: bool = False,
    include_pending: bool = True,
) -> dict:
    """Fetch accounts and transactions from SimpleFIN Bridge."""
    access_url = load_access_url()
    if not access_url:
        raise RuntimeError(
            "No SimpleFIN Access URL configured. Run simplefin_claim_token(setup_token) first."
        )

    parsed = urllib.parse.urlparse(access_url)
    host_port = f"{parsed.hostname}{(':' + str(parsed.port)) if parsed.port else ''}"
    base_url = f"{parsed.scheme}://{host_port}{parsed.path.rstrip('/')}/accounts"

    params = {"version": "2"}
    if include_pending:
        params["pending"] = "1"
    if balances_only:
        params["balances-only"] = "1"
    elif days > 0:
        start_dt = datetime.now(timezone.utc) - timedelta(days=days)
        params["start-date"] = str(int(start_dt.timestamp()))

    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    headers = {"Accept": "application/json", "User-Agent": "jetski-finance-mcp/1.0"}

    if parsed.username:
        user_pass = f"{urllib.parse.unquote(parsed.username)}:{urllib.parse.unquote(parsed.password or '')}"
        b64_auth = base64.b64encode(user_pass.encode("utf-8")).decode("ascii")
        headers["Authorization"] = f"Basic {b64_auth}"

    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=45) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    return payload


def sync_simplefin_to_firestore(days: int = 45) -> dict:
    """Pull all SimpleFIN accounts & transactions (Amex, BofA, SoFi) and store in Firestore."""
    payload = fetch_simplefin_data(days=days, balances_only=False, include_pending=True)
    raw_accounts = payload.get("accounts", [])
    raw_connections = payload.get("connections", [])
    conn_map = {c.get("conn_id"): c for c in raw_connections if c.get("conn_id")}
    errors = payload.get("errors", []) or payload.get("errlist", [])

    db = _get_db()
    accounts_summary = []
    txns_by_period: dict[str, list[dict]] = defaultdict(list)
    payments_by_period: dict[str, list[dict]] = defaultdict(list)

    now_iso = datetime.now(timezone.utc).isoformat()

    for acc in raw_accounts:
        conn = conn_map.get(acc.get("conn_id"), {})
        org = acc.get("org") or {}
        org_name = (
            conn.get("org_name")
            or conn.get("name")
            or org.get("name")
            or org.get("domain")
            or "Bank"
        )
        org_domain = conn.get("org_url") or conn.get("org_id") or org.get("domain") or ""
        institution = _normalize_institution(org_name, org_domain)

        acc_id = acc.get("id", "")
        acc_name = acc.get("name", "Account")
        currency = acc.get("currency", "USD")
        balance = float(acc.get("balance", 0.0) or 0.0)
        avail_raw = acc.get("available-balance")
        available_balance = float(avail_raw) if avail_raw is not None else balance
        bal_date_ts = acc.get("balance-date")
        bal_date = (
            datetime.fromtimestamp(int(bal_date_ts), tz=timezone.utc).strftime("%Y-%m-%d")
            if bal_date_ts
            else now_iso[:10]
        )

        acc_doc = {
            "account_id": acc_id,
            "name": acc_name,
            "institution": institution,
            "institution_name": org_name,
            "currency": currency,
            "balance": round(balance, 2),
            "available_balance": round(available_balance, 2),
            "balance_date": bal_date,
            "updated_at": now_iso,
        }
        if acc_id:
            db.collection(ACCOUNTS_COLLECTION).document(acc_id).set(acc_doc)
        accounts_summary.append(acc_doc)

        for raw_txn in acc.get("transactions", []):
            posted_ts = raw_txn.get("posted") or raw_txn.get("transacted_at")
            if posted_ts:
                dt = datetime.fromtimestamp(int(posted_ts), tz=timezone.utc)
                date_str = dt.strftime("%Y-%m-%d")
                period = dt.strftime("%Y-%m")
            else:
                date_str = now_iso[:10]
                period = now_iso[:7]

            amt = float(raw_txn.get("amount", 0.0) or 0.0)
            desc = (raw_txn.get("description") or raw_txn.get("payee") or "").strip()
            memo = (raw_txn.get("memo") or "").strip()
            full_desc = f"{desc} ({memo})" if memo and memo not in desc else desc
            pending = bool(raw_txn.get("pending", False))
            txn_id = str(raw_txn.get("id", ""))

            # In SimpleFIN, outflows/charges are negative (-$25.00) and inflows/deposits/credits are positive (+$100.00)
            is_inflow = amt > 0
            entry = {
                "txn_id": txn_id,
                "date": date_str,
                "post_date": date_str,
                "description": full_desc,
                "amount": round(abs(amt), 2),
                "signed_amount": round(amt, 2),
                "direction": "inflow" if is_inflow else "outflow",
                "pending": pending,
                "category": "",
                "card_member": f"{institution.upper()} - {acc_name}",
                "institution": institution,
                "account_name": acc_name,
                "account_id": acc_id,
            }

            if is_inflow:
                payments_by_period[period].append(
                    {
                        "txn_id": txn_id,
                        "date": date_str,
                        "amount": round(abs(amt), 2),
                        "description": full_desc,
                        "institution": institution,
                        "account_name": acc_name,
                    }
                )
            else:
                txns_by_period[period].append(entry)

    synced_periods = []
    for period in sorted(set(list(txns_by_period.keys()) + list(payments_by_period.keys()))):
        year, month = int(period[:4]), int(period[5:7])
        _, last_day = monthrange(year, month)

        existing = get_statement(year, month) or {}
        existing_txns = existing.get("transactions", [])

        # Deduplicate by txn_id or (date, description, amount, card_member) while preserving enrichment fields
        merged_map = {}
        for t in existing_txns:
            key = t.get("txn_id") or f"{t.get('date')}|{t.get('description')}|{t.get('amount')}|{t.get('card_member', '')}"
            merged_map[key] = t
        for t in txns_by_period[period]:
            key = t.get("txn_id") or f"{t.get('date')}|{t.get('description')}|{t.get('amount')}|{t.get('card_member', '')}"
            old_t = merged_map.get(key, {})
            merged_t = {**old_t, **t}
            if old_t.get("category") and not t.get("category"):
                merged_t["category"] = old_t["category"]
            merged_map[key] = merged_t

        merged_txns = sorted(merged_map.values(), key=lambda x: x.get("date", ""), reverse=True)
        payments = payments_by_period[period]
        total_debits = sum(t.get("amount", 0.0) for t in merged_txns)
        total_credits = sum(p.get("amount", 0.0) for p in payments)

        statement_doc = {
            "period": period,
            "year": year,
            "month": month,
            "statement_date": f"{year:04d}-{month:02d}-{last_day:02d}",
            "due_date": existing.get("due_date", ""),
            "balance": round(sum(a["balance"] for a in accounts_summary), 2),
            "minimum_due": existing.get("minimum_due", 0.0),
            "previous_balance": existing.get("previous_balance", 0.0),
            "payments": payments,
            "transactions": merged_txns,
            "total_transactions": len(merged_txns),
            "total_debits": round(total_debits, 2),
            "total_credits": round(total_credits, 2),
            "source": "simplefin",
        }
        write_statement(statement_doc)
        synced_periods.append({"period": period, "transactions": len(merged_txns)})

    return {
        "accounts": accounts_summary,
        "synced_periods": synced_periods,
        "errors": errors,
    }


def get_cached_balances() -> list[dict]:
    """Read cached account balances from Firestore."""
    db = _get_db()
    docs = db.collection(ACCOUNTS_COLLECTION).stream()
    return [d.to_dict() for d in docs]
