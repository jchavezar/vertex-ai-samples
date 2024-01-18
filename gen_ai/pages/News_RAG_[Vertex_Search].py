#%%
import vertexai
import pandas as pd
import streamlit as st
from google.cloud import discoveryengine
from google.protobuf.json_format import MessageToDict
from vertexai.language_models import TextGenerationModel
from vertexai.preview.generative_models import GenerativeModel, Part

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "datastore": "the-country_1705604735333"
}

st.title('Retrieval Augmented Generation (RAG) | Vertex Search')
st.image("images/rag_news.png")
st.markdown("[github repo](https://github.com/jchavezar/vertex-ai-samples/tree/main/gen_ai/pages/Financial_RAG_[Vertex_Search].py)")

#region Model Settings
settings = ["text-bison@002", "text-bison-32k@002", "gemini-pro"]
model = st.sidebar.selectbox("Choose a text model", settings)

temperature = st.sidebar.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.2) 
if model == "gemini-pro":
    token_limit = st.sidebar.select_slider("Token Limit", range(1,8193), value=1024)
else:
    token_limit = st.sidebar.select_slider("Token Limit", range(1, 1025), value=256)
top_k = st.sidebar.select_slider("Top-K", range(1, 41), value=40)
top_p = st.sidebar.select_slider("Top-P", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.8) 
    
parameters =  {
    "temperature": temperature,
    "max_output_tokens": token_limit,
    "top_p": top_p,
    "top_k": top_k
    }

with st.sidebar:
    st.markdown(
        """
        Follow me on:

        ldap → [@jesusarguelles](https://moma.corp.google.com/person/jesusarguelles)

        GitHub → [jchavezar](https://github.com/jchavezar)
        
        LinkedIn → [Jesus Chavez](https://www.linkedin.com/in/jchavezar)
        
        Medium -> [jchavezar](https://medium.com/@jchavezar)
        """
    )

#endregion

client = discoveryengine.SearchServiceClient()
serving_config = client.serving_config_path(
    project=variables["project"],
    location=variables["location"],
    data_store=variables["datastore"],
    serving_config="default_config",
    )

def vertex_search(prompt):
    print(prompt)
    #request = discoveryengine.SearchRequest(
    #    serving_config=serving_config, query=prompt, page_size=100)

    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True),
    summary_spec = discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=2, include_citations=True),
    extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
            max_extractive_answer_count=5,
            max_extractive_segment_count=10))

    request = discoveryengine.SearchRequest(
        serving_config=serving_config, query=prompt, page_size=2, content_search_spec=content_search_spec)                                                         

    response = client.search(request)
    
    documents = [MessageToDict(i.document._pb) for i in response.results]

    context = []
    links = []
    pages = []
    for i in documents:
        for ans in i["derivedStructData"]["extractive_answers"]:
            context.append(ans["content"])
            pages.append(ans["pageNumber"])
            links.append("https://storage.mtls.cloud.google.com"+"/".join(i["derivedStructData"]["link"].split("/")[1:]))

    ctx = {
        "contexto": context,
        "links" : links,
        "numbero_pagina": pages
        }
    
    st.markdown("**Contexto Extraído de Vertex Search:**")
    st.dataframe(pd.DataFrame(ctx))
    
    return ctx

def google_llm(prompt, context, model):
    
    template_prompt = f"""Eres un analista de noticias, tus tareas son las siguientes:
    - El contexto contiene la siguiente estructura: contexto, links y numero_pagina.

    Del siguiente contexto encapsulado por comillas: ```{context}```
    
    Responde la siguiente pregunta: {prompt}
    
    Respuesta formato salto de linea: 
    Respuesta: <respuesta>, \n
    Explicación de la Respuesta: <explica como llegaste a la conclusion de tu respuesta> \n
    Referencia: {{pagina: <indica el numero de pagina>, link:<el link de cloud storage>}}
    """
    
    if model != "gemini-pro":
        
        vertexai.init(project="vtxdemos", location="us-central1")
        model = TextGenerationModel.from_pretrained(model)
        response = model.predict(
            template_prompt
            ,
            **parameters
        )
        
    else:
        model = GenerativeModel("gemini-pro")
        response = model.generate_content(
            [template_prompt],
            generation_config=parameters,)
        
    return response.text.replace("$","")

#model = st.radio(
#        "Choose a shipping method",
#        ("text-bison@001", "text-bison")
#    )

with st.form('my_form'):
  text = st.text_area('Enter text:', 'Cual es la fuerza política que se mantuvo al margen durante el debate del congreso?')
  submitted = st.form_submit_button('Submit')
  if submitted:
      context = vertex_search(text)
      st.info(google_llm(text, context, model))


# %%

