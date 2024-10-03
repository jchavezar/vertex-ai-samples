#%%
import json
import vertexai
import pandas as pd
from vertexai.resources.preview import feature_store
from vertexai.generative_models import GenerationConfig, GenerativeModel
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

model_name = "gemini-1.5-flash-002"
embeddings_model_name = "text-embedding-004"
project_id = "vtxdemos"
location = "us-east1"

model = GenerativeModel(model_name=model_name)
vertexai.init(project=project_id, location=location)
fv_text = feature_store.FeatureView(
    name="projects/254356041555/locations/us-east1/featureOnlineStores/feature_store_marketplace/featureViews/etsy_view_text1")
text_emb_model = TextEmbeddingModel.from_pretrained(embeddings_model_name)


# Temporary
from google.cloud import bigquery
df = bigquery.Client().query("select * from `demos_us.etsy-10k-full` limit 100").to_dataframe()

def generate_questions(listing_info: str):
    response_schema = {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "min_items": "4"
            }
        }
    }

    prompt_template = f'''
    You are a helpful product expert for Etsy, proactively prompting customers to discover the breadth of Etsy. 
    Etsy is an e-commerce company with an emphasis on selling of handmade or vintage items and craft supplies.
    You will be provided product information and you need to generate exactly 4 questions using this product information. 
    Questions should be interesting and exciting, but very short.

    <Instructions>
      - 4 questions should be associated with other products that are similar, relevant and compliment this product
    
          List just questions without numbers or hyphens.
          Do not add header,numbers or hyphens
    
    </Instructions>
    '''

    try:
        response = model.generate_content(
            [prompt_template, "\n\n<Product Information>\n", listing_info],
            generation_config=GenerationConfig(
                response_mime_type="application/json", response_schema=response_schema
            ),
        )
        return response.text
    except:
        return "Error"


#%%
def search_for_item_information(query: str):
    """Search for any item information"""

    # Utility Functions
    def response_process(result):
        neighbors = result["neighbors"]

        all_extracted_data = []
        for row in neighbors:
            extracted_data = {}
            extracted_data['text_distance'] = row['distance']  # Extract distance

            for feature in row['entity_key_values']['key_values']['features']:
                name = feature['name']
                if name not in ['ml_generate_embedding_result', 'text_embedding']:
                    if 'value' in feature:
                        for value_type, value in feature['value'].items():
                            extracted_data[name] = value
                    else:
                        extracted_data[name] = "no values"

            all_extracted_data.append(extracted_data)

        dataframe = pd.DataFrame(all_extracted_data)

        return dataframe

    texts = [query]
    inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT") for text in texts]
    embeddings = text_emb_model.get_embeddings(inputs)[0].values

    r = fv_text.search(
        embedding_value=embeddings,
        neighbor_count=16,
        approximate_neighbor_candidates=16,
        leaf_nodes_search_fraction=0.3,
        return_full_entity=True,  # returning entities with metadata
    ).to_dict()

    return response_process(r)

#%%

product_details = df.iloc[50]["content"]
url = df.iloc[50]["image_url"]
print(url)
re = generate_questions(product_details)

print(re)
print(json.loads(re))
#%%
question_cat3 = json.loads(re)["questions"]
#%%
rephraser_prompt_cat3 = '''
    Your task is to rephrase the user's question {question_cat3} to explicitly mention what product it is referring to. 
    Use the information provided in the product information {product_details}. The result should be a single line question.
    '''

print(question_cat3[0])
rephraser_contents_cat3 = [
    rephraser_prompt_cat3,
    question_cat3[0],
    product_details,
]
rephrased_query = model.generate_content(rephraser_contents_cat3)
rephrased_query.text

#%%
new_df = search_for_item_information(rephrased_query.text)

new_df["image_url"].iloc[1]
