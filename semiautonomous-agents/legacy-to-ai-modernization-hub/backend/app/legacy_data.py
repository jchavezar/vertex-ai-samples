"""Legacy 2015 Enterprise ERP Data Generator and Query Simulator."""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import List, Tuple
from .models import LegacyQueryFilter, LegacyRecord


# Sample enterprise entities for legacy 2015 records
COUNTERPARTIES = [
    ("BNPAUS33XXX", "BNP Paribas Global Markets", "EUR", "AAA", "Tier 1", "LCH Clearnet", "FR"),
    ("DEUTDEDDXXX", "Deutsche Bank Ag Frankfurt", "EUR", "AA", "Tier 1", "Eurex Clearing", "DE"),
    ("JPMCUS33XXX", "JPMorgan Chase Treasury Ops", "USD", "AAA", "Tier 1", "CME Group", "US"),
    ("HSBCGB2LXXX", "HSBC Holdings APAC Trade", "GBP", "AA+", "Tier 2", "LCH Clearnet", "GB"),
    ("CITIUS33XXX", "Citigroup North American FX", "USD", "AA-", "Tier 1", "CME Group", "US"),
    ("BARCGB22XXX", "Barclays Capital Liquidity Desk", "GBP", "A+", "Tier 2", "LCH Clearnet", "GB"),
    ("SOCFFRPPXXX", "Societe Generale Prime Brokerage", "EUR", "A", "Tier 2", "Eurex Clearing", "FR"),
    ("UBSWCHZHXXX", "UBS AG Zurich Custodial Desk", "CHF", "AAA", "Tier 1", "SIX x-clear", "CH"),
    ("SMBCJPJTXXX", "Sumitomo Mitsui Banking Corp", "JPY", "A+", "Tier 2", "JSCC Tokyo", "JP"),
    ("ANZBAU3MXXX", "ANZ Banking Group Melbourne", "AUD", "AA-", "Tier 3", "ASX Clear", "AU"),
    ("SANTESMMXXX", "Banco Santander Madrid Treasury", "EUR", "A-", "Tier 3", "BME Clearing", "ES"),
    ("INGBNL2AXXX", "ING Bank N.V. Amsterdam Wholesale", "EUR", "A+", "Tier 2", "Eurex Clearing", "NL"),
    ("BNSCCA44XXX", "Scotiabank Global Commodity Hub", "CAD", "AA", "Tier 2", "ICE Clear", "CA"),
    ("DBSGSGSGXXX", "DBS Bank Singapore Trade Desk", "SGD", "AAA", "Tier 1", "SGX-DC", "SG"),
    ("NDEAFIHHXXX", "Nordea Bank Helsinki Branch", "EUR", "AA-", "Tier 2", "Nasdaq Clearing", "FI"),
    ("STCBLON1XXX", "Standard Chartered Emerging MKTS", "USD", "A", "Tier 3", "LCH Clearnet", "GB"),
    ("BOGTCOBBXXX", "Banco de Bogota Trade Services", "USD", "BBB+", "Tier 4", "Local Bilateral", "CO"),
    ("ITAUCOBRXXX", "Itau Unibanco Sao Paulo Desk", "BRL", "BBB-", "Tier 4", "B3 Clearing", "BR"),
    ("ICBKCNBJXXX", "Industrial & Commercial Bank of China", "CNY", "A+", "Tier 2", "Shanghai Clearing", "CN"),
    ("NBOKKWKWXXX", "National Bank of Kuwait Ops", "USD", "AA-", "Tier 3", "Local Bilateral", "KW"),
]

GL_CODES = [
    ("1010-4490", "Cash & Central Bank Reserves"),
    ("1040-8820", "FX Forward Spot Receivables"),
    ("1080-2210", "Interest Rate Swap Collateral"),
    ("2020-5510", "Cross-Currency Repo Obligations"),
    ("2060-9940", "Short-Term Commercial Paper Notes"),
    ("3010-1120", "Regulatory Tier 1 Capital Reserve"),
    ("4010-3380", "Unsettled Clearing House Margin"),
    ("5010-7730", "Supply Chain Letter of Credit Line"),
]

LIQUIDITY_BUCKETS = ["T+0 (Intraday)", "T+1 (Overnight)", "T+2 to T+7 (1 Week)", "T+8 to T+30 (1 Month)", "T+31 to T+90 (3 Months)", "T+91+ (Long Term)"]
DODD_FRANK_TAGS = ["DF-MANDATORY-CLEAR", "DF-EXEMPT-COMMERCIAL", "DF-BILATERAL-ISDA", "DF-EXCHANGE-TRADED"]
SLA_STATUSES = ["PROCESSED_ON_TIME", "MANUAL_RECON_REQUIRED", "FLAGGED_MARGIN_BREACH", "PENDING_TAX_CLEARANCE", "BATCH_POSTED"]
RECON_FLAGS = ["AUTO_MATCHED_100%", "DISCREPANCY_DELTA_0.02%", "PENDING_SWIFT_ACK", "UNMATCHED_COUNTERPARTY_REF", "POST_CLOSE_EXCEPTION"]

def _generate_deterministic_dataset(count: int = 160) -> List[LegacyRecord]:
    """Generates a stable dataset of 160 realistic enterprise records."""
    random.seed(42)  # Stable deterministic seed
    records: List[LegacyRecord] = []
    base_date = datetime(2015, 6, 15)

    for i in range(1, count + 1):
        cp_tuple = COUNTERPARTIES[i % len(COUNTERPARTIES)]
        gl_tuple = GL_CODES[i % len(GL_CODES)]
        bic, cp_name, curr, risk, margin, clearing, jur = cp_tuple
        
        # calculate notional
        amount = round(random.uniform(250_000, 48_500_000), 2)
        spread = round(random.uniform(1.2, 38.5), 2)
        risk_weight = round(random.choice([20.0, 50.0, 75.0, 100.0, 150.0]), 1)
        
        settle_offset = (i * 3) % 90
        settle_dt = base_date + timedelta(days=settle_offset)
        audit_dt = base_date - timedelta(days=1, hours=random.randint(1, 23), minutes=random.randint(1, 59))
        
        rec = LegacyRecord(
            transaction_id=f"TX-2015-{i:06d}",
            gl_code=f"{gl_tuple[0]} ({gl_tuple[1]})",
            counterparty_bic=bic,
            counterparty_name=cp_name,
            settlement_date=settle_dt.strftime("%Y-%m-%d"),
            currency=curr,
            notional_amount=amount,
            fx_spread_bps=spread,
            clearing_house=clearing,
            margin_tier=margin,
            risk_rating=risk,
            liquidity_bucket=LIQUIDITY_BUCKETS[i % len(LIQUIDITY_BUCKETS)],
            tax_jurisdiction=jur,
            dodd_frank_tag=DODD_FRANK_TAGS[i % len(DODD_FRANK_TAGS)],
            basel_risk_weight_pct=risk_weight,
            sla_status=SLA_STATUSES[i % len(SLA_STATUSES)],
            audit_timestamp=audit_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            batch_id=f"BATCH-EOD-201506-{i % 12 + 1:02d}",
            reconciliation_flag=RECON_FLAGS[i % len(RECON_FLAGS)],
            override_notes=f"Approved by VP Risk Auth #{1000 + i % 50}; Manual override standard limits" if i % 7 == 0 else "System verified standard booking"
        )
        records.append(rec)
    return records


ALL_LEGACY_RECORDS = _generate_deterministic_dataset(160)


async def query_legacy_database(query_filter: LegacyQueryFilter) -> Tuple[List[LegacyRecord], int, float]:
    """
    Simulates a 2015 enterprise relational DB query with intentional latency.
    """
    start_time = time.perf_counter()

    # Simulate legacy database I/O latency
    if query_filter.simulate_slow_query_ms > 0:
        await asyncio.sleep(query_filter.simulate_slow_query_ms / 1000.0)

    filtered = ALL_LEGACY_RECORDS

    if query_filter.search:
        s = query_filter.search.lower()
        filtered = [
            r for r in filtered
            if s in r.transaction_id.lower()
            or s in r.counterparty_name.lower()
            or s in r.counterparty_bic.lower()
            or s in r.gl_code.lower()
            or s in r.currency.lower()
        ]

    if query_filter.currency:
        filtered = [r for r in filtered if r.currency.upper() == query_filter.currency.upper()]

    if query_filter.risk_rating:
        filtered = [r for r in filtered if r.risk_rating.upper() == query_filter.risk_rating.upper()]

    if query_filter.margin_tier:
        filtered = [r for r in filtered if query_filter.margin_tier.lower() in r.margin_tier.lower()]

    if query_filter.clearing_house:
        filtered = [r for r in filtered if query_filter.clearing_house.lower() in r.clearing_house.lower()]

    if query_filter.sla_status:
        filtered = [r for r in filtered if query_filter.sla_status.lower() in r.sla_status.lower()]

    total_count = len(filtered)
    start_idx = (query_filter.page - 1) * query_filter.page_size
    end_idx = start_idx + query_filter.page_size
    page_data = filtered[start_idx:end_idx]

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return page_data, total_count, elapsed_ms
