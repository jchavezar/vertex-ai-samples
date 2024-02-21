#%%
import sys
sys.path.append("..")
import re
import httpx
import vertexai
from utils import sockcop_vertexai
from vertexai.language_models import TextGenerationModel
from vertexai.preview.generative_models import GenerativeModel, Part

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "data_store_id": "countries-and-their-cultur_1706277976842"
}


parameters = {
    "candidate_count": 1,
    "max_output_tokens": 1024,
    "temperature": 1,
    "top_k": 40
}

client = sockcop_vertexai.Client(variables)
unicorn_model = TextGenerationModel.from_pretrained("text-unicorn@001")
gemini_model = GenerativeModel("gemini-pro")

class Chatbot:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        
        if self.system:
            self.messages.append("Context: {}".format(system))
            
    
    def __call__(self, message):
        self.messages.append(message)
        result = self.execute()
        self.messages.append(result)
        return result
    
    def execute(self):
        print("\n".join(self.messages))
        response = unicorn_model.predict("\n".join(self.messages), **parameters)
        return response.text
    
prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

wikipedia:
e.g. wikipedia: Django
Returns a summary from searching Wikipedia

rag_search:
e.g. rag_search: Countries [Mexico, Spain, England, etc]
Returns information about arts, culture, history, ethnic groups, anthropology, of countries.

summarization:
e.g. summarization: <returns/response from previous steps>
Returns a summarization

Always look things up on Wikipedia if you have the opportunity to do so.

Example session:

Question: What is the capital of France?
Thought: I should look up France on Wikipedia
Action: wikipedia: France
PAUSE

You will be called again with this:

Observation: France is a country. The capital is Paris.

You then output:

Answer: The capital of France is Paris
""".strip()

def wikipedia(q):
    return httpx.get("https://en.wikipedia.org/w/api.php", params={
        "action": "query",
        "list": "search",
        "srsearch": q,
        "format": "json"
    }).json()["query"]["search"][0]["snippet"]

def rag(q):
    return client.vertex_search(q)

def summarization(prompt):
    response =  gemini_model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.9,
            "top_p": 1
            },
        )
  
    return response.text

known_actions = {
    "wikipedia": wikipedia,
    "rag_search": rag,
    "summarization": summarization
}

action_re = re.compile('^Action: (\w+): (.*)$')

def query(question, max_turns=10):
    i = 0
    bot = Chatbot(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot("Question: {}".format(next_prompt))
        print(result)
        actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
        if actions:
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print(" -- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return

#%%
query("Explain the culture about samurais")

# %%
