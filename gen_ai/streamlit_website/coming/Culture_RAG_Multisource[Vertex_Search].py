#%%
import sys
sys.path.append('..')
from utils import sockcop_vertexai
import time
from typing import Dict
from vertexai.language_models import TextGenerationModel

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "data_store_id": "countries-and-their-cultur_1706277976842"
}

client = sockcop_vertexai.Client(variables)

parameters = {
    "candidate_count": 1,
    "max_output_tokens": 1024,
    "temperature": 0,
    "top_p": 0.5
}


prompt_template = '''
You are a LLM that detects intents from user queries. Your task is to classify the user's intents based on their query. Below are the possible intents with brief descriptions. Use these to accurately determine the user's goal, and output only the intent or intents topic.

- Country Population: Inquiries about the total number midyear population per country during 2023.
- Country Culture: Questions about the arts, culture, history, ethnic groups, anthropology, location and geography, etc.
- Feedback: User comments, reviews, or general feedback about services, or experiences.
- Other: Choose this if the query does not fall into any of the other intents.

User Query:
How many days are in a month.

Response:
["Other"].

User Query:
I would like to check my last order and give feedback.

Response:
["Order status", "Feedback"].

User Query:
'''

def intent_detection(query: str, parameters: Dict) -> str:
    model = TextGenerationModel.from_pretrained("text-bison@002")
    response = model.predict(
        prompt_template+query,
        **parameters
        )
    return response.text

start = time.time()
print(intent_detection("Tell me about the arts and culture of the top 10 most populated countries", parameters=parameters))
print(time.time()-start)
# %%


client.vertex_search("Tell me about the arts and culture of the top 10 most populated countries")
# %%
