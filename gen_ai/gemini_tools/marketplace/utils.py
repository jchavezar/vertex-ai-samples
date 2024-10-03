#%%
import json
import vertexai
import pandas as pd
from vertexai.resources.preview import feature_store
from vertexai.generative_models import GenerationConfig, GenerativeModel, SafetySetting
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

model_name = "gemini-1.5-flash-001"
embeddings_model_name = "text-embedding-004"
project_id = "vtxdemos"
location = "us-east1"

model = GenerativeModel(
    model_name=model_name,
    generation_config={"temperature": 1.1}
)
vertexai.init(project=project_id, location=location)
fv_text = feature_store.FeatureView(
    name="projects/254356041555/locations/us-east1/featureOnlineStores/feature_store_marketplace/featureViews/etsy_view_text_v1_1")
text_emb_model = TextEmbeddingModel.from_pretrained(embeddings_model_name)

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

class Gemini:
    def __init__(self):
        self.retrieval_results = None
        self.dataframe = None
        self.response_schema = {
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

        self.prompt_template = """
        You are a helpful product expert for Etsy, proactively prompting customers to discover the breadth of Etsy. 
        Etsy is an e-commerce company with an emphasis on selling of handmade or vintage items and craft supplies.
        You will be provided product information and you need to generate exactly 4 questions using this product information.
        Questions should be interesting and exciting, but very short.
        
        <Instructions>
        - 4 questions should be associated with other products that are similar, relevant and compliment this product
        
        List just questions without numbers or hyphens.
        Do not add header,numbers or hyphens  
        </Instructions>
        """

        self.rephraser_prompt_cat3 = """
        Your task is to rephrase the user's question {question_cat3} to explicitly mention what product it is referring to. 
        Use the information provided in the product information {product_details}. The result should be a single line question.
        """

    def generate_questions(self, listing_info):
        try:
            response = model.generate_content(
                [self.prompt_template, "\n\n<Product Information>\n", listing_info],
                generation_config=GenerationConfig(
                    response_mime_type="application/json", response_schema=self.response_schema, temperature=1.1
                ),
                safety_settings=safety_settings
            )
            return response.text
        except:
            print("Error")
            return 'error'

    def response_process(self, result):
        neighbors = result["neighbors"]

        all_extracted_data = []
        for row in neighbors:
            extracted_data = {'text_distance': row['distance']}

            for feature in row['entity_key_values']['key_values']['features']:
                name = feature['name']
                if name not in ['ml_generate_embedding_result', 'text_embedding']:
                    if 'value' in feature:
                        for value_type, value in feature['value'].items():
                            extracted_data[name] = value
                    else:
                        extracted_data[name] = "no values"

            all_extracted_data.append(extracted_data)

        self.dataframe = pd.DataFrame(all_extracted_data)

        #dataframe = pd.DataFrame(all_extracted_data)

    def search_for_item_information(self, query):
        texts = [query]
        inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT") for text in texts]
        embeddings = text_emb_model.get_embeddings(inputs)[0].values

        r = fv_text.search(
            embedding_value=embeddings,
            neighbor_count=4,
            approximate_neighbor_candidates=4,
            leaf_nodes_search_fraction=0.3,
            return_full_entity=True,  # returning entities with metadata
        ).to_dict()

        self.response_process(r)

    def run(self, content):
        recommendations = []
        re = self.generate_questions(content)
        if re != "error":
            question_cat3 = json.loads(re)["questions"]
            for num, question in enumerate(question_cat3):
                rephraser_contents_cat3 = [
                    self.rephraser_prompt_cat3,
                    question,
                    content,
                ]
                print(num)
                rephrased_query = model.generate_content(rephraser_contents_cat3, safety_settings=safety_settings, generation_config={"temperature": 1.1}).text
                self.search_for_item_information(rephrased_query)
                recommendations.append({"rephraser_question": rephrased_query, "dataframe": self.dataframe})
        return recommendations




