#%%
import sys
import json
import pandas as pd
from google.cloud import bigquery

sys.path.append("./marketplace")
import vertexai
from vertexai.preview.generative_models import grounding, Tool
#from utils import generate_questions, search_for_item_information
from utils import Gemini
from vertexai.generative_models import GenerativeModel, GenerationConfig, SafetySetting

# Temporary Table
from google.cloud import bigquery

project_id = "vtxdemos"
table_id = "demos_us.etsy_10k"
# noinspection SqlDialectInspection
df = bigquery.Client(project=project_id).query(f"select * from `{table_id}`").to_dataframe()
vertexai.init(project=project_id, location="us-east1")
cat3_gemini = Gemini()

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

#%%
# Questions Category 1
system_instructions_cat_1 = """
You are a helpful product expert for Etsy, proactively prompting customers to discover the breadth of Etsy. 
Etsy is an e-commerce company with an emphasis on selling of handmade or vintage items and craft supplies.
You will be provided product information and you need to generate exactly 12 questions using this product information. 
Questions should be interesting and exciting, but very short.

<Instructions>
  - 4 questions MUST be related to the product that customers usually ask about that product.
      Questions should be directly relevant to the product, addressing typical customer inquiries about its features, specifications, or usage as suggested by product details.
      Make questions very short and the created questions MUST have answers within product information.
      Do not ask very explicit questions.
  - Create 4 answers to these questions by looking up product information (context).
</Instructions>
"""

system_instructions_cat_2 = """
You are a helpful product expert for Etsy, proactively prompting customers to discover the breadth of Etsy. 
Etsy is an e-commerce company with an emphasis on selling of handmade or vintage items and craft supplies.
You will be provided product information and you need to generate exactly 12 questions using this product information. 
Questions should be interesting and exciting, but very short.

<Instructions>
  - 4 questions should be associated with this product information but completely beyond the explicit product details, exploring potential applications, key features to consider, material properties, historical context, or broader industry standards
      These questions should pique the customer's interest and encourage them to explore the product.
      Should be very general questions for which you can search in Google Search to provide needed information
      DO not ask questions about product availability or prices.
  - Create 4 answers to these questions by using Google Search.
</Instructions>

"""

response_schema_cat1 = {
    "type": "OBJECT",
    "properties": {
        "questions_cat1": {
            "type": "ARRAY",
            "items": {
                "type": "STRING"
            },
            "min_items": 4,
            "max_items": 4
        },
        "answers_cat1": {
            "type": "ARRAY",
            "items": {
                "type": "STRING"
            },
            "min_items": 4,
            "max_items": 4
        }
    },
    "required": ["questions_cat1", "answers_cat1"]
}

response_schema_cat2 = {
    "type": "OBJECT",
    "properties": {
        "questions_cat2": {
            "type": "ARRAY",
            "items": {
                "type": "STRING"
            },
            "min_items": 4,
            "max_items": 4
        },
        "answers_cat2": {
            "type": "ARRAY",
            "items": {
                "type": "STRING"
            },
            "min_items": 4,
            "max_items": 4
        },
    },
    "required": ["questions_cat2", "answers_cat2"]
}

tools = [
    Tool.from_google_search_retrieval(
        google_search_retrieval=grounding.GoogleSearchRetrieval()
    ),
]

context_model = GenerativeModel(
    "gemini-1.5-flash-001",
    generation_config=GenerationConfig(temperature=1.1, response_mime_type="application/json",
                                       response_schema=response_schema_cat1),
    system_instruction=system_instructions_cat_1,
)

ground_model = GenerativeModel(
    "gemini-1.5-flash-001",
    generation_config=GenerationConfig(
        temperature=1.1,
        response_mime_type="application/json",
        response_schema=response_schema_cat2,
        max_output_tokens=4000),
    tools=tools,
    system_instruction=system_instructions_cat_2
)

#%%
# Concatenation of Rows
df["concatenated_product_info"] = df.apply(lambda x:
                                           f"""Title: {x['title']}, Description: {x['description']}, Price: {x['price_usd']}, Tags: {x['tags']}, Materials: {x['materials']}, Attributes: {x['attributes']}, Category: {x['category']}
                                           """,
                                           axis=1)
df_final = df.drop_duplicates(subset=["listing_id"])

#%%
## Create Category 1 Q&A
df_100 = df_final.copy()  # Create an explicit copy
df_100.loc[:100, "category_1"] = df_100.loc[:100, "concatenated_product_info"].apply(
    lambda row: context_model.generate_content(["Product Details:\n", row], safety_settings=safety_settings).text)

#%%
## Create Category 2 Q&A
df_100.loc[:100, "category_2"] = df_100.loc[:100, "concatenated_product_info"].apply(
    lambda row: ground_model.generate_content(["Product Details:\n", row], safety_settings=safety_settings).text)
final_df = df_100.iloc[:100]

#%%
## Create Category 3 Q&A
recommendations = cat3_gemini.run(df_final.iloc[1]["concatenated_product_info"])

#%%
for rec in recommendations:
    print("Rephraser Question: ", rec["rephraser_question"])
    for index, row in rec["dataframe"].iterrows():
        print(f"Title: {row['title']}")
        print(f"Image URL: {row['image_url']}")

#%%
###
df_100 = df_final.copy()
results = {}

_questions_cat_1 = []
_questions_cat_2 = []
_questions_cat_3 = []
_listings_id = []

for index, row in df_100.iloc[:200].iterrows():
    print(index)
    questions_cat_1 = context_model.generate_content(["Product Details:\n", row["concatenated_product_info"]], safety_settings=safety_settings).text
    questions_cat_2 = ground_model.generate_content(["Product Details:\n", row["concatenated_product_info"]], safety_settings=safety_settings).text
    recommendations = cat3_gemini.run(df_final.iloc[1]["concatenated_product_info"])
    rec_list = []
    for rec in recommendations:
        rephrased_question = rec["rephraser_question"]
        titles = []
        image_urls = []
        listing_ids = []
        for i, r in rec["dataframe"].iterrows():
            titles.append(r["title"])
            image_urls.append(r["image_url"])
            listing_ids.append(r["listing_id_1"])
        rec_list.append({"rephrased_question": rephrased_question, "titles": titles, "image_urls": image_urls,
                         "listing_ids": listing_ids})
    reclist = json.dumps(rec_list)

    _questions_cat_1.append(questions_cat_1)
    _questions_cat_2.append(questions_cat_2)
    _questions_cat_3.append(reclist)
    _listings_id.append(row["listing_id"])


d = pd.DataFrame(
    {
        "cat_1": _questions_cat_1,
        "cat_2": _questions_cat_2,
        "cat_3": _questions_cat_3,
        "listing_id": _listings_id
    }
)

#%% Store and Add to BQ
d.to_csv("gs://vtxdemos-datasets-private/marketplace/dataset.csv")

bigquery.Client(project=project_id).load_table_from_dataframe(d, destination="demos_us.etsy_v1_1_200rows", job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"))

#%%
sql_query_embeddings = """
CREATE OR REPLACE TABLE
  `demos_us.etsy_embeddings_v1_1_200rows` AS (
  SELECT
    *
  FROM
    ML.GENERATE_EMBEDDING( MODEL `demos_us.text_embedding_044`,
      (
      SELECT
        *,
        CASE
          WHEN title IS NULL AND listing_id IS NULL AND description IS NULL AND price_usd IS NULL AND tags IS NULL AND materials IS NULL AND attributes IS NULL AND category IS NULL THEN "" -- All NULL, return empty string
          ELSE CASE
          WHEN title IS NOT NULL THEN "Product Title: " || CAST(title AS STRING) || " "
          ELSE ""
      END
        ||
        CASE
          WHEN listing_id IS NOT NULL THEN "Product Listing id: " || CAST(listing_id AS STRING) || " "
          ELSE ""
      END
        ||
        CASE
          WHEN description IS NOT NULL THEN "Product Description: " || CAST(description AS STRING) || " "
          ELSE ""
      END
        ||
        CASE
          WHEN price_usd IS NOT NULL THEN "Price: " || CAST(price_usd AS STRING) || " "
          ELSE ""
      END
        ||
        CASE
          WHEN tags IS NOT NULL THEN "Product Tags: " || CAST(tags AS STRING) || " "
          ELSE ""
      END
        ||
        CASE
          WHEN materials IS NOT NULL THEN "Product Materials: " || CAST(materials AS STRING) || " "
          ELSE ""
      END
        ||
        CASE
          WHEN attributes IS NOT NULL THEN "Product Attributes: " || CAST(attributes AS STRING) || " "
          ELSE ""
      END
        ||
        CASE
          WHEN category IS NOT NULL THEN "Product Category: " || CAST(category AS STRING)
          ELSE ""
      END
      END
        AS content
      FROM (
        SELECT
          q.listing_id,
          o.* EXCEPT(listing_id)
        FROM
          `demos_us.etsy_v1_1_200rows` q
        INNER JOIN
          `demos_us.etsy_10k` o
        ON
          q.listing_id = o.listing_id)) ) )
"""

bigquery.Client(project=project_id).query(sql_query_embeddings).result()