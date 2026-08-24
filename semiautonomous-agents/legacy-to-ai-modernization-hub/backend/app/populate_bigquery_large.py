"""Generate 300+ realistic enterprise rows for each BigQuery demo table."""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ID = os.getenv("GCP_PROJECT", "vtxdemos")
DATASET_ID = f"{PROJECT_ID}.ebc_modernization_demo"

client = bigquery.Client(project=PROJECT_ID)

random.seed(42)

# Vendors & Suppliers
VENDORS = [
    {"id": "V-8821", "name": "TSMC Advanced Wafer Fab", "country": "TW", "tier": "CRITICAL"},
    {"id": "V-9942", "name": "Foxconn Precision Optoelectronics", "country": "TW", "tier": "CRITICAL"},
    {"id": "V-7714", "name": "ASE Technology Packaging", "country": "TW", "tier": "CRITICAL"},
    {"id": "V-6631", "name": "MediaTek Silicon Design", "country": "TW", "tier": "WATCH"},
    {"id": "V-5520", "name": "Delta Electronics Power Solutions", "country": "TW", "tier": "STABLE"},
    {"id": "V-4411", "name": "Pegatron Assembly Systems", "country": "TW", "tier": "WATCH"},
    {"id": "V-1020", "name": "Texas Instruments Dallas", "country": "US", "tier": "STABLE"},
    {"id": "V-1030", "name": "Qualcomm Wireless Systems", "country": "US", "tier": "STABLE"},
    {"id": "V-1040", "name": "Analog Devices Boston", "country": "US", "tier": "STABLE"},
    {"id": "V-2040", "name": "Monterrey Precision Assembly", "country": "MX", "tier": "STABLE"},
    {"id": "V-2050", "name": "Guadalajara Electronic Interconnect", "country": "MX", "tier": "STABLE"},
    {"id": "V-3010", "name": "Infineon Technologies Munich", "country": "DE", "tier": "STABLE"},
    {"id": "V-3020", "name": "Bosch Mobility Electronics", "country": "DE", "tier": "STABLE"},
    {"id": "V-4010", "name": "Tokyo Electron Lithography", "country": "JP", "tier": "STABLE"},
    {"id": "V-4020", "name": "Murata Manufacturing Components", "country": "JP", "tier": "STABLE"},
    {"id": "V-5010", "name": "Samsung Semiconductor Hwaseong", "country": "KR", "tier": "WATCH"},
    {"id": "V-5020", "name": "SK Hynix Memory Systems", "country": "KR", "tier": "WATCH"},
]

PART_CATEGORIES = [
    ("WAFER-3NM-SOC", "3nm Heterogeneous Core SoC", "Semiconductors", 450000.0, 950000.0),
    ("SUBSTRATE-FCBGA", "High-Density Flip-Chip BGA Substrate", "Substrates", 120000.0, 380000.0),
    ("OPTIC-LENS-8K", "Precision LiDAR & Optical Sensor Lens", "Sensors", 85000.0, 240000.0),
    ("CHASSIS-TITANIUM", "Aerospace Titanium Enclosure CNC", "Mechanical", 150000.0, 420000.0),
    ("PKG-SIP-256", "System-in-Package 256-Ball Interconnect", "Packaging", 95000.0, 310000.0),
    ("MEM-HBM3E-16G", "HBM3e Ultra-Bandwidth Memory Stack 16GB", "Memory", 280000.0, 750000.0),
    ("MODEM-5G-SAT", "Satellite & 5G Telemetry RF Module", "Wireless", 65000.0, 190000.0),
    ("PMIC-POWER-GEN4", "Multi-Phase High-Efficiency Power IC", "Power", 42000.0, 140000.0),
    ("CAP-CERAMIC-0402", "Automotive Grade MLCC Capacitors (Reel)", "Passives", 15000.0, 65000.0),
    ("MCU-AUTOMOTIVE-32", "32-Bit Dual-Core Automotive MCU", "Semiconductors", 110000.0, 320000.0),
    ("DIODE-SIC-1200V", "Silicon Carbide Power Diode 1200V", "Power", 75000.0, 210000.0),
    ("FPGA-HIGH-DENSITY", "High-Density FPGA Compute Accelerator", "Compute", 350000.0, 890000.0),
]

BANKS = [
    ("DBS Bank Singapore", "FAC-DBS-APAC-01", "DBSGSG2X"),
    ("Standard Chartered HK", "FAC-SCB-HK-02", "SCBLHKHH"),
    ("Citigroup Taipei", "FAC-CITI-TW-01", "CITITWTW"),
    ("BNP Paribas Paris", "FAC-BNP-EU-03", "BNPAFRPP"),
    ("HSBC Holdings London", "FAC-HSBC-UK-01", "MIDLGB22"),
    ("JPMorgan Chase NY", "FAC-JPMC-US-01", "CHASUS33"),
    ("BBVA Mexico", "FAC-BBVA-MX-01", "BCMRMXMM"),
    ("MUFG Bank Tokyo", "FAC-MUFG-JP-01", "BOTKJPJT"),
    ("Deutsche Bank Frankfurt", "FAC-DB-DE-01", "DEUTDEDD"),
    ("Santander Madrid", "FAC-SAN-ES-01", "BSCHESMM"),
]

def generate_large_datasets():
    print("Generating large enterprise datasets (250 - 400 rows each)...")
    base_date = datetime(2026, 6, 1)

    # 1. PROCUREMENT PO COMMITMENTS (320 rows)
    proc_rows = []
    for i in range(1, 321):
        v = random.choice(VENDORS)
        p = random.choice(PART_CATEGORIES)
        notional = round(random.uniform(p[3], p[4]) * random.randint(10, 60), 2)
        deadline = base_date + timedelta(days=random.randint(15, 180))
        status = random.choices(["OPEN", "IN_TRANSIT", "PENDING_CUSTOMS", "FULFILLED"], weights=[0.65, 0.20, 0.10, 0.05])[0]
        
        proc_rows.append({
            "po_id": f"PO-2026-{v['country']}-{i:04d}",
            "vendor_id": v["id"],
            "vendor_name": v["name"],
            "supplier_country": v["country"],
            "part_code": p[0],
            "part_name": p[1],
            "category": p[2],
            "notional_usd": notional,
            "status": status,
            "delivery_deadline": deadline.strftime("%Y-%m-%d"),
            "shipping_port": "Kaohsiung" if v["country"] == "TW" else ("Rotterdam" if v["country"] == "DE" else ("Manzanillo" if v["country"] == "MX" else "Long Beach")),
            "payment_terms": random.choice(["NET_30", "NET_60", "LC_AT_SIGHT", "CAD"]),
        })

    df_proc = pd.DataFrame(proc_rows)
    table_id_proc = f"{DATASET_ID}.procurement_po_commitments"
    client.load_table_from_dataframe(df_proc, table_id_proc, job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")).result()
    print(f"✓ Table {table_id_proc} populated: {len(df_proc)} rows")

    # 2. INVENTORY POSITIONS (260 rows)
    inv_rows = []
    for i in range(1, 261):
        v = random.choice(VENDORS)
        p = random.choice(PART_CATEGORIES)
        sku = f"{p[0]}-G{random.randint(1, 5)}"
        
        # Make Taiwan components have realistic low safety stock if critical
        if v["country"] == "TW" and p[0] in ["WAFER-3NM-SOC", "SUBSTRATE-FCBGA", "PKG-SIP-256", "MEM-HBM3E-16G"]:
            safety_stock = random.randint(28, 44)
            stoppage_risk = "CRITICAL_BOTTLENECK"
        else:
            safety_stock = random.randint(45, 120)
            stoppage_risk = "MODERATE_EXPOSURE" if safety_stock < 60 else "LOW_EXPOSURE"

        burn_rate = random.randint(120, 950)
        inv_val = round(burn_rate * safety_stock * random.uniform(180, 850), 2)

        inv_rows.append({
            "part_sku": sku,
            "base_part_code": p[0],
            "part_name": p[1],
            "supplier_id": v["id"],
            "supplier_name": v["name"],
            "supplier_country": v["country"],
            "warehouse_facility": random.choice(["WH-AUSTIN-01", "WH-MONTERREY-03", "WH-FRANKFURT-02", "WH-TAIPEI-01"]),
            "safety_stock_days": safety_stock,
            "daily_burn_rate_units": burn_rate,
            "inventory_value_usd": inv_val,
            "stoppage_risk": stoppage_risk,
            "reorder_trigger_level": random.randint(30, 50),
        })

    df_inv = pd.DataFrame(inv_rows)
    table_id_inv = f"{DATASET_ID}.inventory_positions"
    client.load_table_from_dataframe(df_inv, table_id_inv, job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")).result()
    print(f"✓ Table {table_id_inv} populated: {len(df_inv)} rows")

    # 3. TREASURY FX DERIVATIVES (280 rows)
    treasury_rows = []
    ccy_pairs = [
        ("USD/TWD", 31.40, 32.25),
        ("EUR/USD", 1.082, 1.095),
        ("USD/JPY", 153.5, 156.8),
        ("USD/MXN", 18.15, 18.65),
        ("GBP/USD", 1.265, 1.285),
        ("USD/KRW", 1360.0, 1395.0),
    ]

    for i in range(1, 281):
        pair_info = random.choice(ccy_pairs)
        pair = pair_info[0]
        bank = random.choice(BANKS)
        fwd_rate = round(random.uniform(pair_info[1], pair_info[2]), 4)
        spot_rate = round(fwd_rate * random.uniform(0.985, 1.015), 4)
        notional = round(random.uniform(1500000.0, 35000000.0), 2)
        mat_date = base_date + timedelta(days=random.randint(20, 240))
        
        # Taiwan currency contracts (USD/TWD) has explicit UNHEDGED ones
        if pair == "USD/TWD":
            hedge_status = random.choices(["UNHEDGED", "HEDGED_SWAP", "HEDGED_COLLAR", "HEDGED_FORWARD"], weights=[0.35, 0.25, 0.20, 0.20])[0]
        else:
            hedge_status = random.choices(["HEDGED_SWAP", "HEDGED_COLLAR", "HEDGED_FORWARD", "UNHEDGED"], weights=[0.40, 0.30, 0.20, 0.10])[0]

        treasury_rows.append({
            "deal_id": f"FX-2026-{pair.replace('/', '')}-{i:04d}",
            "currency_pair": pair,
            "notional_amount_usd": notional,
            "forward_rate": fwd_rate,
            "spot_rate": spot_rate,
            "maturity_date": mat_date.strftime("%Y-%m-%d"),
            "hedge_status": hedge_status,
            "counterparty_bank": bank[0],
            "facility_id": bank[1],
            "swift_bic": bank[2],
            "isda_master_agreement": "ISDA-2002-MULTI",
            "collateral_threshold_m": round(random.uniform(5.0, 20.0), 1),
        })

    df_tr = pd.DataFrame(treasury_rows)
    table_id_tr = f"{DATASET_ID}.treasury_fx_derivatives"
    client.load_table_from_dataframe(df_tr, table_id_tr, job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")).result()
    print(f"✓ Table {table_id_tr} populated: {len(df_tr)} rows")

    print("===============================================================")
    print(f"✅ Successfully Populated 860+ Rows Across BigQuery in {DATASET_ID}!")
    print("===============================================================")

if __name__ == "__main__":
    generate_large_datasets()
