"""Populate real BigQuery tables for the EBC Modernization Hub demo."""

import os
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ID = os.getenv("GCP_PROJECT", "vtxdemos")
DATASET_ID = f"{PROJECT_ID}.ebc_modernization_demo"

client = bigquery.Client(project=PROJECT_ID)

def populate_tables():
    print(f"Creating and populating real BigQuery tables in {DATASET_ID}...")

    # 1. Procurement PO Commitments Table
    procurement_data = [
        {"po_id": "PO-2026-TW-001", "vendor_id": "V-8821", "vendor_name": "TSMC Advanced Wafer Fab", "supplier_country": "TW", "part_code": "WAFER-3NM-SOC", "part_name": "3nm Heterogeneous Core SoC", "notional_usd": 65000000.0, "status": "OPEN", "delivery_deadline": "2026-07-15"},
        {"po_id": "PO-2026-TW-002", "vendor_id": "V-8821", "vendor_name": "TSMC Advanced Wafer Fab", "supplier_country": "TW", "part_code": "SUBSTRATE-FCBGA", "part_name": "High-Density Substrate", "notional_usd": 42500000.0, "status": "OPEN", "delivery_deadline": "2026-07-28"},
        {"po_id": "PO-2026-TW-003", "vendor_id": "V-9942", "vendor_name": "Foxconn Precision Optoelectronics", "supplier_country": "TW", "part_code": "OPTIC-LENS-8K", "part_name": "Precision Sensor Lens Module", "notional_usd": 38200000.0, "status": "OPEN", "delivery_deadline": "2026-08-04"},
        {"po_id": "PO-2026-TW-004", "vendor_id": "V-9942", "vendor_name": "Foxconn Precision Optoelectronics", "supplier_country": "TW", "part_code": "CHASSIS-TITANIUM", "part_name": "Aerospace Grade Enclosure", "notional_usd": 29800000.0, "status": "OPEN", "delivery_deadline": "2026-08-18"},
        {"po_id": "PO-2026-TW-005", "vendor_id": "V-7714", "vendor_name": "ASE Technology Packaging", "supplier_country": "TW", "part_code": "PKG-SIP-256", "part_name": "System-in-Package Interconnect", "notional_usd": 34100000.0, "status": "OPEN", "delivery_deadline": "2026-08-25"},
        {"po_id": "PO-2026-TW-006", "vendor_id": "V-7714", "vendor_name": "ASE Technology Packaging", "supplier_country": "TW", "part_code": "MEM-HBM3E-16G", "part_name": "HBM3e Memory Stack 16GB", "notional_usd": 51400000.0, "status": "OPEN", "delivery_deadline": "2026-09-02"},
        {"po_id": "PO-2026-TW-007", "vendor_id": "V-6631", "vendor_name": "MediaTek Silicon Design", "supplier_country": "TW", "part_code": "MODEM-5G-SAT", "part_name": "Satellite Telemetry Modem", "notional_usd": 24800000.0, "status": "OPEN", "delivery_deadline": "2026-09-10"},
        {"po_id": "PO-2026-TW-008", "vendor_id": "V-6631", "vendor_name": "MediaTek Silicon Design", "supplier_country": "TW", "part_code": "PMIC-POWER-GEN4", "part_name": "Smart Power Management IC", "notional_usd": 18200000.0, "status": "OPEN", "delivery_deadline": "2026-09-20"},
        {"po_id": "PO-2026-US-001", "vendor_id": "V-1020", "vendor_name": "Texas Instruments Dallas", "supplier_country": "US", "part_code": "ANALOG-AMPLIFIER", "part_name": "High-Voltage Analog Amp", "notional_usd": 15600000.0, "status": "OPEN", "delivery_deadline": "2026-07-20"},
        {"po_id": "PO-2026-MX-001", "vendor_id": "V-2040", "vendor_name": "Monterrey Precision Assembly", "supplier_country": "MX", "part_code": "HARNESS-AUTO-PRO", "part_name": "Heavy Vehicle Wiring Harness", "notional_usd": 22400000.0, "status": "OPEN", "delivery_deadline": "2026-08-10"},
    ]
    df_proc = pd.DataFrame(procurement_data)
    table_id_proc = f"{DATASET_ID}.procurement_po_commitments"
    client.load_table_from_dataframe(df_proc, table_id_proc, job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")).result()
    print(f"✓ Table {table_id_proc} populated ({len(df_proc)} rows)")

    # 2. Inventory Positions Table
    inventory_data = [
        {"part_sku": "WAFER-3NM-SOC", "part_name": "3nm Heterogeneous Core SoC", "supplier_id": "V-8821", "supplier_name": "TSMC Advanced Wafer Fab", "supplier_country": "TW", "safety_stock_days": 38, "daily_burn_rate_units": 450, "inventory_value_usd": 24500000.0, "stoppage_risk": "CRITICAL_BOTTLENECK"},
        {"part_sku": "SUBSTRATE-FCBGA", "part_name": "High-Density Substrate", "supplier_id": "V-8821", "supplier_name": "TSMC Advanced Wafer Fab", "supplier_country": "TW", "safety_stock_days": 42, "daily_burn_rate_units": 620, "inventory_value_usd": 18200000.0, "stoppage_risk": "HIGH_EXPOSURE"},
        {"part_sku": "OPTIC-LENS-8K", "part_name": "Precision Sensor Lens Module", "supplier_id": "V-9942", "supplier_name": "Foxconn Precision Optoelectronics", "supplier_country": "TW", "safety_stock_days": 45, "daily_burn_rate_units": 310, "inventory_value_usd": 12400000.0, "stoppage_risk": "HIGH_EXPOSURE"},
        {"part_sku": "CHASSIS-TITANIUM", "part_name": "Aerospace Grade Enclosure", "supplier_id": "V-9942", "supplier_name": "Foxconn Precision Optoelectronics", "supplier_country": "TW", "safety_stock_days": 55, "daily_burn_rate_units": 200, "inventory_value_usd": 16500000.0, "stoppage_risk": "MODERATE_EXPOSURE"},
        {"part_sku": "PKG-SIP-256", "part_name": "System-in-Package Interconnect", "supplier_id": "V-7714", "supplier_name": "ASE Technology Packaging", "supplier_country": "TW", "safety_stock_days": 34, "daily_burn_rate_units": 800, "inventory_value_usd": 14200000.0, "stoppage_risk": "CRITICAL_BOTTLENECK"},
        {"part_sku": "MEM-HBM3E-16G", "part_name": "HBM3e Memory Stack 16GB", "supplier_id": "V-7714", "supplier_name": "ASE Technology Packaging", "supplier_country": "TW", "safety_stock_days": 40, "daily_burn_rate_units": 550, "inventory_value_usd": 29800000.0, "stoppage_risk": "CRITICAL_BOTTLENECK"},
        {"part_sku": "MODEM-5G-SAT", "part_name": "Satellite Telemetry Modem", "supplier_id": "V-6631", "supplier_name": "MediaTek Silicon Design", "supplier_country": "TW", "safety_stock_days": 60, "daily_burn_rate_units": 150, "inventory_value_usd": 8900000.0, "stoppage_risk": "LOW_EXPOSURE"},
        {"part_sku": "PMIC-POWER-GEN4", "part_name": "Smart Power Management IC", "supplier_id": "V-6631", "supplier_name": "MediaTek Silicon Design", "supplier_country": "TW", "safety_stock_days": 50, "daily_burn_rate_units": 380, "inventory_value_usd": 6700000.0, "stoppage_risk": "MODERATE_EXPOSURE"},
    ]
    df_inv = pd.DataFrame(inventory_data)
    table_id_inv = f"{DATASET_ID}.inventory_positions"
    client.load_table_from_dataframe(df_inv, table_id_inv, job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")).result()
    print(f"✓ Table {table_id_inv} populated ({len(df_inv)} rows)")

    # 3. Treasury FX Derivatives Table
    treasury_data = [
        {"deal_id": "FX-2026-TWD-088", "currency_pair": "USD/TWD", "notional_amount_usd": 8500000.0, "forward_rate": 31.45, "spot_rate": 32.10, "maturity_date": "2026-07-20", "hedge_status": "UNHEDGED", "counterparty_bank": "DBS Bank Singapore", "facility_id": "FAC-DBS-APAC-01"},
        {"deal_id": "FX-2026-TWD-094", "currency_pair": "USD/TWD", "notional_amount_usd": 5700000.0, "forward_rate": 31.52, "spot_rate": 32.15, "maturity_date": "2026-08-15", "hedge_status": "UNHEDGED", "counterparty_bank": "Standard Chartered Hong Kong", "facility_id": "FAC-SCB-HK-02"},
        {"deal_id": "FX-2026-TWD-101", "currency_pair": "USD/TWD", "notional_amount_usd": 25000000.0, "forward_rate": 31.20, "spot_rate": 32.10, "maturity_date": "2026-09-10", "hedge_status": "HEDGED_SWAP", "counterparty_bank": "Citigroup Taipei", "facility_id": "FAC-CITI-TW-01"},
        {"deal_id": "FX-2026-EUR-045", "currency_pair": "EUR/USD", "notional_amount_usd": 45000000.0, "forward_rate": 1.085, "spot_rate": 1.092, "maturity_date": "2026-07-30", "hedge_status": "HEDGED_COLLAR", "counterparty_bank": "BNP Paribas Paris", "facility_id": "FAC-BNP-EU-03"},
        {"deal_id": "FX-2026-JPY-012", "currency_pair": "USD/JPY", "notional_amount_usd": 18000000.0, "forward_rate": 154.20, "spot_rate": 156.40, "maturity_date": "2026-08-25", "hedge_status": "HEDGED_FORWARD", "counterparty_bank": "MUFG Bank Tokyo", "facility_id": "FAC-MUFG-JP-01"},
        {"deal_id": "FX-2026-MXN-008", "currency_pair": "USD/MXN", "notional_amount_usd": 12000000.0, "forward_rate": 18.25, "spot_rate": 18.45, "maturity_date": "2026-09-15", "hedge_status": "HEDGED_FORWARD", "counterparty_bank": "BBVA Mexico", "facility_id": "FAC-BBVA-MX-01"},
    ]
    df_tr = pd.DataFrame(treasury_data)
    table_id_tr = f"{DATASET_ID}.treasury_fx_derivatives"
    client.load_table_from_dataframe(df_tr, table_id_tr, job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")).result()
    print(f"✓ Table {table_id_tr} populated ({len(df_tr)} rows)")

    print("===============================================================")
    print("✅ Real BigQuery Tables Initialized Successfully in vtxdemos!")
    print("===============================================================")

if __name__ == "__main__":
    populate_tables()
