#%%
import vertexai
import requests
from bs4 import BeautifulSoup
from vertexai.language_models import TextGenerationModel
from vertexai.preview.generative_models import GenerativeModel, Part

model = GenerativeModel("gemini-pro")

def get_answer(url, question):
  page = requests.get(url).content
  text = BeautifulSoup(page.decode(), 'lxml').text
  
  print(text)

  prompt_ask = f'''Answer the question : {question}, based on the below context \n Context : {text} \n ''' # correct

  reponse = model.generate_content(
      [prompt_ask],
      generation_config = {"temperature": 0.2, "top_k":40, "top_p":0.8}
      )
  return reponse.text

response = get_answer("https://elpais.com/", "dame un resumen del contexto?")

#def google_llm(prompt, context, chat_history, model):
#  
#    template_prompt = f"""
#    Contexto:
#    - Eres una AI analista de noticias, trata de mantener una conversacion entre tu y el humano:
#    - Utiliza unicamente la fuente informativa como la unica verdad, no inventes cosas que no vengan de la fuente.
#    - La fuente contiene la siguiente estructure: contexto, links y numero_pagina.
#    - La fuente es la siguiente y esta encapsulada por comillas: ```{context}```
#    - Este es el historial de la conversacion empleada hasta el momento: {chat_history}
#    
#    Tarea:
#    - Responde la siguiente pregunta: {prompt}
#  
#    Respuesta formato salto de linea: 
#    Respuesta: <respuesta>, \n
#    Explicación de la Respuesta: <explica como llegaste a la conclusion de tu respuesta> \n
#    Referencia: {{ pagina: <indica el numero de pagina>, link:<el link de cloud storage> }}
#    """
#  
#    if model != "gemini-pro":
#      
#        vertexai.init(project="vtxdemos", location="us-central1")
#        model = TextGenerationModel.from_pretrained(model)
#        response = model.predict(
#            template_prompt
#            ,
#            **parameters
#        )
#      
#    else:
#        model = GenerativeModel("gemini-pro")
#        response = model.generate_content(
#            [template_prompt],
#            generation_config=parameters,)
#      
#    return response.text.replace("$","")

# %%
