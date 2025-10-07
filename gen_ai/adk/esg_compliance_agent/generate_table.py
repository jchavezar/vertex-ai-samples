#%%
import os
import json
from google import genai
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import pandas as pd
from io import StringIO

BIGQUERY_DATASET = "esg_demo_data"
BIGQUERY_TABLE_MASTER = "esg_procurement_master"

bq_client = bigquery.Client()

PRE_PROMPT_GOOGLE_SEARCH = """
I am creating synthetic/realistic data for ESG (Environmental, Social, and Governance) to become carbon neutral in 
big companies with thousands of employees, your main task is to find out the most recent office/datacenter hardware like
laptops, cell phones, monitors, keyboards, cameras, mouses, also switches, routers, access points and everything you
think can increase the carbon in a big company with many employees, generate a list of products with the model and brand
and specs.

add apple products like iphones and macbooks, imacs etc, android like chromebooks and pixels.

I need at least 40 different laptops models.
"""

print("Generating Data for the Synthetic Table")
client = genai.Client(vertexai=True, project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"), location="global")
research_response = client.models.generate_content(
    model="gemini-2.5-flash-preview-09-2025",
    contents=PRE_PROMPT_GOOGLE_SEARCH,
    config=genai.types.GenerateContentConfig(
        tools=[genai.types.Tool(google_search=genai.types.GoogleSearch())]
    )
)

GENERATE_SYNTHETIC_DATA_MARKDOWN = f"""
Role: Generate a complete synthetic data table for a Deloitte ESG demo.
Task: Create a single table with exactly 60 unique rows. The output MUST be a CSV-formatted markdown table with column headers. DO NOT include any text before or after the table.

Columns MUST be: Transaction_ID, Supplier_Name, Product_Name, Total_Cost_USD, Purchase_Date, S_Labor_Compliance, E_Carbon_Scope3, G_Board_Diversity.

General Constraint: Ensure that at least four of the five Product_Name entries are specific, latest-model electronic devices (laptops, monitors, cell phones, etc.) released in 2025, using plausible names like 'MacBook Pro 16-inch M4 (2025)' or 'Samsung Odyssey G10 Monitor (2025)'. 
Use this information for your produces: 
## INFORMATION ##
{research_response.text}
## END OF INFORMATION ##

The 5 rows must cover these critical scenarios. Use plausible product names and numbers for 2025:
Row 1 (FAIL CASE): High-value IT hardware purchase (Total_Cost_USD > 700000). The Product_Name must be a high-volume order of a 2025 model laptop. S_Labor_Compliance score MUST be 65.
Row 2 (SUCCESS CASE): High-value IT hardware purchase (Total_Cost_USD > 500000) with Product_Name being a high-volume order of a 2025 model cell phone or tablet. S_Labor_Compliance score MUST be 88.
Row 3 (PREFERRED ALTERNATIVE): Low-emissions item. The Product_Name must be a refurbished or EPEAT Gold Certified electronic device (e.g., 'Refurbished Studio Display 2025'). E_Carbon_Scope3 must be low (around 1.5).
Row 4 (GOVERNANCE RISK): Purchase of a high-end monitor or workstation from a supplier with G_Board_Diversity less than 0.35.
Row 5 (ENVIRONMENTAL RISK): Purchase from a travel/logistics supplier with E_Carbon_Scope3 above 15.0.
"""

#%%
output_schema = {
    "type": "object",
    "properties": {
        "esg_procurement_data": {
            "type": "array",
            "description": "A complete synthetic data table for a Deloitte ESG demo, containing exactly 60 unique procurement records. The data must adhere to the specific scenarios for the first five rows.",
            # minItems and maxItems have been removed to resolve the 'Constraint is too tall' error.
            "items": {
                "type": "object",
                "properties": {
                    "Transaction_ID": {
                        "type": "string",
                        "description": "A unique identifier for the procurement transaction (e.g., '1', '2', etc.)."
                    },
                    "Supplier_Name": {
                        "type": "string",
                        "description": "The name of the supplier."
                    },
                    "Product_Name": {
                        "type": "string",
                        "description": "The name of the product or service. Must include specific 2025 electronic device models for at least four of the first five rows."
                    },
                    "Total_Cost_USD": {
                        "type": "number",
                        "description": "The total cost of the purchase in USD. Must be > 700000 for Row 1 and > 500000 for Row 2."
                    },
                    "Purchase_Date": {
                        "type": "string",
                        "description": "The date of the purchase in 'YYYY-MM-DD' format."
                    },
                    "S_Labor_Compliance": {
                        "type": "integer",
                        "description": "The Social Labor Compliance score. Must be 65 for Row 1 and 88 for Row 2."
                    },
                    "E_Carbon_Scope3": {
                        "type": "number",
                        "description": "The Environmental Carbon Scope 3 emissions value. Must be around 1.5 for Row 3 and above 15.0 for Row 5."
                    },
                    "G_Board_Diversity": {
                        "type": "number",
                        "description": "The Governance Board Diversity ratio (0.0 to 1.0). Must be less than 0.35 for Row 4."
                    }
                },
                "required": [
                    "Transaction_ID",
                    "Supplier_Name",
                    "Product_Name",
                    "Total_Cost_USD",
                    "Purchase_Date",
                    "S_Labor_Compliance",
                    "E_Carbon_Scope3",
                    "G_Board_Diversity"
                ]
            }
        }
    },
    "required": [
        "esg_procurement_data"
    ]
}

print("Generating Synthetic Data")
client = genai.Client(vertexai=True, project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"), location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))
re = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=GENERATE_SYNTHETIC_DATA_MARKDOWN,
    config=genai.types.GenerateContentConfig(
        response_json_schema=output_schema,
        response_mime_type="application/json",
    )
)

#%%
df = pd.DataFrame(json.loads(re.text)["esg_procurement_data"])
df.head()

#%%
def ensure_dataset_exists(dataset_id):
    dataset_ref = bq_client.dataset(dataset_id)
    try:
        bq_client.get_dataset(dataset_ref)
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        bq_client.create_dataset(dataset)

def load_dataframe_to_bq(df, table_name, bq_schema):
    df['Purchase_Date'] = pd.to_datetime(df['Purchase_Date'], errors='coerce').dt.strftime('%Y-%m-%d')

    df.dropna(subset=['Transaction_ID', 'Supplier_Name', 'Total_Cost_USD'], inplace=True)

    destination_table = f"{bq_client.project}.{BIGQUERY_DATASET}.{table_name}"

    table_ref = bq_client.dataset(BIGQUERY_DATASET).table(table_name)

    try:
        bq_client.get_table(table_ref)
    except NotFound:
        table = bigquery.Table(table_ref, schema=bq_schema)
        bq_client.create_table(table)
        print(f"Created table {destination_table}")

    csv_data = df.to_csv(index=False)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=False,
        schema=bq_schema,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    try:
        job = bq_client.load_table_from_file(
            StringIO(csv_data),
            table_ref,
            job_config=job_config
        )
        job.result()
        print(f"Successfully loaded {len(df)} rows into {destination_table}.")
    except Exception as e:
        print(f"BigQuery Load Failed for {destination_table}: {e}")


MASTER_SCHEMA = [
    bigquery.SchemaField("Transaction_ID", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("Supplier_Name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("Product_Name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("Total_Cost_USD", "NUMERIC", mode="REQUIRED"),
    bigquery.SchemaField("Purchase_Date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("S_Labor_Compliance", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("E_Carbon_Scope3", "NUMERIC", mode="REQUIRED"),
    bigquery.SchemaField("G_Board_Diversity", "NUMERIC", mode="REQUIRED"),
]

ensure_dataset_exists(BIGQUERY_DATASET)

load_dataframe_to_bq(df, BIGQUERY_TABLE_MASTER, MASTER_SCHEMA)