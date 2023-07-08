## LLM Models Helpers
import ast
import vertexai
import streamlit as st
from vertexai.language_models import TextGenerationModel

class ai:
    def __init__(self):
       self.model = TextGenerationModel.from_pretrained("text-bison@001")
       self.params = {"temperature": 0.1, "max_output_tokens": 256, "top_p": 0.8, "top_k": 40}


    def get_questions_for_gatter_att(self):
      vertexai.init(project="vtxdemos", location="us-central1")
      parameters = self.params
      model = self.model
      response = model.predict(
          f"""Perform the following actions:
          - Identify the topics from the following text (keep the response for future instructions dont print it out):
          hi there I am 28 years old from Venezuela, married to a Veteran with no kids yet but 2 puppies that love with all my heart. I speak English and Spanish. Just moved from Florida back to California. I have over 10 years of experience with kids up to 12 years old, infants and toddlers. my last job lasted a year and a half and I was a nanny for two beautiful girls (nanny sharing). I am comfortable with pets. I am very loving and caring and I can say I am very patient. Love doing art and crafts of all kinds. Love cooking and Baking. Enjoy going for walks specially if they end at the park. I am a very responsible person and believe that communication is the key for a relationship nanny-parents or sitter-parents. You can contact me through here or ask for my number
          - Avoid the following topics: 
          [Age, Marital Status, Languages Spoken, Location]
          -  Create 5 different questions you should ask for creating a new similar text, respond in the following python format:
          [question 1, question 2, ]
            """,
          **parameters
      )
      #return response.text
      return ast.literal_eval(response.text)

      

      "this is a dictionary with your general information like name, age, genre and language, use it in the bio: <{basic_info}>"