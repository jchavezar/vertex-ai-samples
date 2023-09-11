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
            "temperature": 0.2,
            "max_output_tokens": 256,
            "top_p": 0.8,
            "top_k": 40
        }
    
    def extract_topics(self, text):
        params = {
            "temperature": 0.2,
            "max_output_tokens": 1024,
            "top_p": 0.8,
            "top_k": 20
            }
        #print(text)
        response = self.model.predict(
            """Context: Following list have some example topics for a biographical summary:
        - name
        - education_level
        - hobbies
        - skills
        - number_of_years_of_experience
        - language
        - ...

        Instructions: 
        1 - From the following biographical summary create a list of up to 6 topics detected, the list above is an example do not take it as requisite, if there is no topic detected do not output it.
        2 - Create questions you should ask to the topics detected, do not repeat similar questions, and remove questions with empty answers or NA.
        3 - From the questions above create a brief summary as an answer do not exceed 6 words.
        {text}

        Only use the following format as output, do not use \"Summary\" in your output:

        Output format Python Dictionary: {{\"topic1\": {{\"question\": <question>, \"answer\": <answer>}}, \"<topic2>\": {{\"question\": <question>, \"answer\": <answer>}} }}""".format(text=text),
            **params
        )
        response = response.text.strip("`")
        response = re.sub(' +', ' ', response)
        response = re.sub('\n +', ' ', response)
        response = re.sub('\s +', '', response)
        response = re.sub(r'(.*[A-z])(")([A-z].*)', r'\1 \3', response)
        response = re.sub(r"(.*[A-z])(')([A-z].*)", r"\1 \3", response)
        #print(response)
        return ast.literal_eval(response.strip())
    

    def create_profile(self, form, bio_strong_text):
        import streamlit as st
        response = self.model.predict(
            f"""Context: 
            You are a caregiver looking for creating a very friendly, funny and passionate biographical summary.

            Instructions:

            Given the following care_bios_data enclosed by backticks, create a biographical summary in the style of the example_summary enclosed by asterisk.
            Be as detailed as possible.

        <care_bios_data>: ```{form}```

        <example_summary>: ***{bio_strong_text}***
        
        Output text paragraph:
        """,
            **self.default_parameters
        )
        #print("LLM Model Job Runing")
        return response.text
    
    def additional_questions(self, bios, old_questions):
        params = {
            "temperature": 0.8,
            "max_output_tokens": 256,
            "top_p": 0.8,
            "top_k": 40
        }
        response = self.model.predict(
            """Instruction:
        From the following biographical summary:

        Provided data:
        {bios}
        
        Do the following:

        Forbidden type questions: Do not create anything regarding rate, rates or pricing.

        - Create 2 other questions you should ask to get a stronger biographical summary, do not create any question related to these: {old_questions}.
        - Create synthetic answers for questions above.

        Output JSON Format: 
        """.format(bios=bios, old_questions=old_questions),
            **params
        )
        import streamlit as st
        #print("LLM Model Job Runing - additional questions")
        response = response.text.strip("`")
        response = re.sub(' +', ' ', response)
        response = re.sub('\n +', ' ', response)
        response = re.sub('\s +', '', response)
        response = re.sub(r'(.*[A-z])(")([A-z].*)', r'\1 \3', response)
        response = re.sub(r"(.*[A-z])(')([A-z].*)", r"\1 \3", response)
        return ast.literal_eval(response.strip())

# %%
