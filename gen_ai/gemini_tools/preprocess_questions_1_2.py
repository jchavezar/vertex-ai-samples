#%%
import vertexai
from vertexai.preview.generative_models import grounding, Tool
#from utils import generate_questions, search_for_item_information
from utils import Gemini
from vertexai.generative_models import GenerativeModel, GenerationConfig

# Temporary Table
from google.cloud import bigquery
project_id = "vtxdemos"
table_id = "demos_us.etsy_10k"
# noinspection SqlDialectInspection
df = bigquery.Client(project=project_id).query(f"select * from `{table_id}`").to_dataframe()
vertexai.init(project=project_id, location="us-east1")
cat3_gemini = Gemini()

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
            }
        },
        "answers_cat1": {
            "type": "ARRAY",
            "items": {
                "type": "STRING"
            }
        }
    }
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
    generation_config=GenerationConfig(temperature=1, response_mime_type="application/json", response_schema=response_schema_cat1),
    system_instruction=system_instructions_cat_1
)

ground_model = GenerativeModel(
    "gemini-1.5-flash-001",
    generation_config=GenerationConfig(
        temperature=1,
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
df_100.loc[:100, "category_1"] = df_100.loc[:100, "concatenated_product_info"].apply(lambda row: context_model.generate_content(["Product Details:\n", row]).text)

#%%
## Create Category 2 Q&A
df_100.loc[:100, "category_2"] = df_100.loc[:100, "concatenated_product_info"].apply(lambda row: ground_model.generate_content(["Product Details:\n", row]).text)
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