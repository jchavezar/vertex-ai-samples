#%%
import vertexai
import pandas as pd
import streamlit as st
from utils.links_references import *
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

def app(model, parameters):
    st.title('Retrieval Augmented Generation (RAG) | Vertex Search')
    st.image("images/rag_news.png")
    st.markdown(f""" :green[repo:] [![Repo]({github_icon})]({news_elpais_qa})""")


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
        
    with st.expander("Acerca la Aplicación"):
        st.write("""
                 Se utilizaron los siguientes documentos para aumentar el contexto del modelo:
                 - [Vox Acentúa su Radicalismo y Vota Contra la Reforma Constitucional](https://storage.googleapis.com/vtxdemos-vertex-search-dataset/el_pais/vox_el_pais_jan_18.pdf)
                 - [La Unión Europea Trabaja con la Organización Marítima]( https://storage.googleapis.com/vtxdemos-vertex-search-dataset/el_pais/ue_pellets.pdf
                 Preguntas ejemplo:
                 - Qué es `Vox`?
                 - Quién es el lider de `Vox`?
                 - Cuál fué el término sustituído en el `artículo 49` durante la asamblea?
                 - Cuál fué la propuesta legislativa en la costa norte española?
                 - Por qué el comisario de Océanos, Pesca y Medio Ambiente, le llamó `catástrofe ecológica`?
                 - Quién es `Teresa Ribera`
                 Código Fuente: [github repo](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/pages/News_RAG_%5BVertex_Search%5D%5BConversational%5D.py)
                 """)

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
        Referencia: {{ pagina: <indica el numero de pagina>, link:<el link de cloud storage> }}
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
      text = st.text_area('Enter text:', 'Cuál es la fuerza política que se mantuvo al margen durante el debate del congreso?')
      submitted = st.form_submit_button('Submit')
      if submitted:
          context = vertex_search(text)
          st.info(google_llm(text, context, model))

    # %%

