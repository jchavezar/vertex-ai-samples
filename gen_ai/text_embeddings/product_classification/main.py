#%%
import os
import csv
import numpy as np
import pandas as pd
from google import genai
from google.genai import types
from google.cloud import bigquery

project = "vtxdemos"
location = "us-central1"
emb_model = "text-embedding-005"
gen_model = "gemini-2.5-flash-preview-04-17"
dataset_id = "private"
table_id = "verano"

df = pd.read_csv("florida_connecticut_product_name_examples.csv")

client = genai.Client(
    vertexai=True,
    project=project,
    location=location
)

bq_client = bigquery.Client(project=project)

# Function to generate embeddings from text
def generate_embeddings(text: str):
    response = client.models.embed_content(
        model=emb_model,
        contents=[
            text
        ],
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=768,
            title="Product Classification",
        ),
    )
    return response.embeddings[0].values

#%%


# Create an embeddings Database from unique names.
mapped_names = list(df["mapped_name"].unique())  # Unique Names for Mapped Name
emb_mapped_names = [{name: generate_embeddings(name)} for name in mapped_names]
database = np.array([list(d.values())[0] for d in emb_mapped_names])  # Numpy Array with Vectors

np.save("database.npy", database)  # Store Locally


# Line by line text construct
def similarity(text: str):
    product_emb = np.array(generate_embeddings(text))
    prod_similar = np.dot(database, product_emb)
    most_similar_index = np.argmax(prod_similar)
    most_similar_product_name = mapped_names[most_similar_index]
    highest_similarity_score = prod_similar[most_similar_index]
    return most_similar_product_name, highest_similarity_score


def process_row(row):
    text_to_embed = f"""
    Product Name: {row["product_name"]}, 
    Brand: {row["brand"]}, 
    SubCategory: {row["sub_category"]}, 
    Product Weight: {row["product_weight"]}"""
    return similarity(text_to_embed)


#%%
# Generate embeddings for each row and their score (2150 products/rows).
df[["emb_product", "emb_score"]] = df.apply(process_row, axis=1, result_type='expand')

#%%
# Using GenAI

config = types.GenerateContentConfig(
    system_instruction=
    f"""
        Your mission is to classify the products based on the following table {mapped_names},
        
        The product can come in packets like 5x2g, so take into account the total weight of the box.
        Pay special attention to the weight (1 means 1g, 0.100 means 100mg and the product_name where sometimes
        it comes with the quantity so the weight can vary, it has to be the total weight when expressed like this (quantityXweight in mg or g)).
    """,
    thinking_config=types.ThinkingConfig(
        thinking_budget=0
    )
)

iteration_counter = 0

def gen_ai_process_row(row):
    global iteration_counter
    try:
        iteration_counter += 1
        re = client.models.generate_content(
            model=gen_model,
            config=config,
            contents=f"""Classify the following product:
            Product Name: {row["product_name"]},
            Brand: {row["brand"]},
            SubCategory: {row["sub_category"]},
            Product Weight: {row["product_weight"]}
            """
        )
        if iteration_counter % 20 == 0:
            print(f"Iteration {iteration_counter}: {re.text}")
        return re.text
    except Exception as e:
        print(f"Error: {e}")
        return None


df["gen_ai_class"] = df.apply(gen_ai_process_row, axis=1, result_type='expand')

df.to_csv("result_embeddings.csv", index=False)

#%%
# Copy to BigQuery
table_ref = bq_client.dataset(dataset_id).table(table_id)

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
)

job = bq_client.load_table_from_dataframe(
    df, table_ref, job_config=job_config)
