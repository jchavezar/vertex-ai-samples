#%%
import re
import ast
import vertexai
from vertexai.language_models import TextGenerationModel

class LLM:
    def __init__(self):
        vertexai.init(project="vtxdemos", location="us-central1")
        self.model = TextGenerationModel.from_pretrained("text-bison")
        self.default_parameters = {
            "temperature": 0.8,
            "max_output_tokens": 256,
            "top_p": 0.8,
            "top_k": 40
        }
        
    #def get_attributes(self, text, params=None):
    #    if params == None:
    #        params = self.default_parameters
    #    response = self.model.predict(
    #        f"""You're a caregiver and want to get the attributes/skills that better describes you using the following text enclosed by <>:
    #        
    #    Text: <{text}>
    #
    #    Response Format as python list of adjectives (no more than 10 words) and if you have 2 words join them by '_':""",
    #    **params  
    #    )
    #    print(text)
    #    print("********************\n")
    #    print(f"Response from Model: {response.text}")
    #    return ast.literal_eval(response.text)
    #         [{{'topic':\'topic 'name'\','question':\'question\','answer':\'answer as a python list\'}}]


    def extract_topics(self, text):
        params = {
            "temperature": 0.2,
            "max_output_tokens": 1024,
            "top_p": 0.8,
            "top_k": 20
            }
        response = self.model.predict(
            """Create a list limited to 5 most important with the topics detected in the following text, then create questions you should ask to get similar topics, if you don't know the answer just say 'no info provided':

        Output format in python list of dictionaries: [{{'topic':'<Name>', 'question':'<question>', 'answer':'<answer>'}}, ...]

        input: Education Level
        output: Bachelors, Masters, High School

        input: Languages
        output: English, Mandarin, Spanish

        input: Hobbies
        output: Music, reading

        input: Number of years of experience
        output: 5, 10, 2

        input: Passionate/love/enjoy
        output: bonding, caring, playing

        input: {text}
        output:
        """.format(text=text.replace("'","")),
            **params
        )
        response = response.text.replace("'", '"')
        response = re.sub(' +', ' ', response)
        response = re.sub('\n +', ' ', response)
        print(response)
        return eval(response)
    
    def create_profile(self, text):
        response = self.model.predict(
    f"""You\'re a caregiver who needs to create a strong and convincent profile bios, use the following information to create one:
    {text}
    """,
    **self.default_parameters
    )
        print("LLM Model Job Runing")
        print(type(response.text))
        print(response.text.replace("'", '"'))
        return response.text

