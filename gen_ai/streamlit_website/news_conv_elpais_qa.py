#%%
import vertexai
import pandas as pd
import streamlit as st
from google.cloud import discoveryengine
from google.protobuf.json_format import MessageToDict
from vertexai.language_models import TextGenerationModel
from vertexai.preview.generative_models import GenerativeModel, Part

news_source = ""
code_string = '''
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

client = discoveryengine.SearchServiceClient()
serving_config = client.serving_config_path(
    project=variables["project"],
    location=variables["location"],
    data_store=variables["datastore"],
    serving_config="default_config",
    )

def vertex_search(prompt):
    print(prompt)
    request = discoveryengine.SearchRequest(
        serving_config=serving_config, query=prompt, page_size=100)
 
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
            links.append("https://storage.googleapis.com"+"/".join(i["derivedStructData"]["link"].split("/")[1:]))

    ctx = {
        "contexto": context,
        "links" : links,
        "pagina": pages
        }
    
    num = 0
    ctx_ = {}
    
    for i in documents:
        for ans in i["derivedStructData"]["extractive_answers"]:
            num += 1
            _link = "https://storage.googleapis.com"+"/".join(i["derivedStructData"]["link"].split("/")[1:])
            _texto = ans["content"]
            _pagina = ans["pageNumber"]
            ctx_[f"contexto: {num}"]="texto: {}, fuente: {}, pagina: {}".format(_texto, _link, _pagina)
    
    print(ctx_)
    
    return ctx_

def google_llm(prompt, context, chat_history, model):
  
    template_prompt = f"""
    Contexto:
    - Eres una AI analista de noticias MUY AMIGABLE, trata de mantener una conversacion entre tu y el humano:
    - Utiliza unicamente la fuente informativa como la unica verdad, no inventes cosas que no esten en la fuente.
    - La fuente es la siguiente (y esta encapsulada por triple comillas: ```{context}```
    - Del contexto extrae el link y la pagina para tu respuesta.
    - Este es el historial de la conversacion empleada hasta el momento: {chat_history}
    
    Tarea:
    - Responde o Ejecuta lo siguiente encapsulada por doble comillas: ``{prompt}``
  
    Respuesta formato salto de linea: 
    Respuesta: <respuesta>, \n
    Explicación de la Respuesta: <explica como llegaste a la conclusion de tu respuesta> \n
    Referencia: {{ link:<el link de cloud storage>, pagina: <numero de pagina extraida del contexto>,}}
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

with st.container():
        
    if "model" not in st.session_state:
        st.session_state["model"] = model
        
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
        
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("Pregunta algo"):
        st.session_state.chat_history.append({"role": "human_2", "content": prompt})
        
        with st.chat_message("human_2"):
            st.markdown(prompt)
            
        with st.chat_message("ai_2.0"):
            full_response = ""
            message_placeholder = st.empty()
            
            news_source = vertex_search(st.session_state.chat_history[-1]["content"])
            human_last_message = [st.session_state.chat_history[n]["content"] for n,i in enumerate(st.session_state.chat_history) if i["role"] == "human_2"][-1]
            response = google_llm(prompt=human_last_message, context=news_source, chat_history=st.session_state.chat_history , model=st.session_state["model"])

            full_response += (response or "")
            message_placeholder.markdown(full_response + "▌")
        st.session_state.chat_history.append({"role": "ai_2.0", "content": full_response})

'''

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "datastore": "the-country_1705604735333"
}

def app(model, parameters):
    with st.container():
        st.title('Generación Aumentada de Recuperación (inglés: RAG) | Vertex Search')
        st.image("images/rag_news.png")

        with st.expander("Acerca la Aplicación"):
            st.write("""
                     Se utilizaron los siguientes documentos para aumentar el contexto del modelo:
                     - [Vox Acentúa su Radicalismo y Vota Contra la Reforma Constitucional](https://storage.googleapis.com/vtxdemos-vertex-search-dataset/el_pais/vox_el_pais_jan_18.pdf)
                     - [La Unión Europea Trabaja con la Organización Marítima]( https://storage.googleapis.com/vtxdemos-vertex-search-dataset/el_pais/ue_pellets.pdf)

                     Preguntas ejemplo:
                     - Qué es `Vox`?
                     - Quién es el lider de la `Vox`?
                     - Cuál fué el término sustituído en el `artículo 49` durante la asamblea?
                     - Cuál fué la propuesta legislativa en la costa norte española?
                     - Por qué el comisario de Océanos, Pesca y Medio Ambiente, le llamó `catástrofe ecológica`?
                     - Quién es `Teresa Ribera`?

                     Código Fuente: [github repo](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/pages/News_RAG_%5BVertex_Search%5D%5BConversational%5D.py)
                     """)

        with st.expander("Muéstrame el Código"):
            st.code(code_string, language='python')

    ##region Model Settings
    #settings = ["text-bison@002", "text-bison-32k@002", "gemini-pro"]
    #model = st.sidebar.selectbox("Choose a text model",  settings, key="elpais_model_1")
#
    #temperature = st.sidebar.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="elpais_model_2", value=0.2) 
    #if model == "gemini-pro":
    #    token_limit = st.sidebar.select_slider("Token Limit", range(1,8193), key="elpais_token_1", value=1024)
    #else:
    #    token_limit = st.sidebar.select_slider("Token Limit", range(1, 1025), key="elpais_token_2", value=256)
    #top_k = st.sidebar.select_slider("Top-K", range(1, 41), key="elpais_topk_1", value=40)
    #top_p = st.sidebar.select_slider("Top-P", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="elpais_topk_p", value=0.8) 
#
    #parameters =  {
    #    "temperature": temperature,
    #    "max_output_tokens": token_limit,
    #    "top_p": top_p,
    #    "top_k": top_k
    #    }
#
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
        request = discoveryengine.SearchRequest(
            serving_config=serving_config, query=prompt, page_size=100)
    
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
                links.append("https://storage.googleapis.com"+"/".join(i["derivedStructData"]["link"].split("/")[1:]))

        ctx = {
            "contexto": context,
            "links" : links,
            "pagina": pages
            }

        num = 0
        ctx_ = {}

        for i in documents:
            for ans in i["derivedStructData"]["extractive_answers"]:
                num += 1
                _link = "https://storage.googleapis.com"+"/".join(i["derivedStructData"]["link"].split("/")[1:])
                _texto = ans["content"]
                _pagina = ans["pageNumber"]
                ctx_[f"contexto: {num}"]="texto: {}, fuente: {}, pagina: {}".format(_texto, _link, _pagina)

        print(ctx_)

        return ctx_

    def google_llm(prompt, context, chat_history, model):
    
        template_prompt = f"""
        Contexto:
        - Eres una AI analista de noticias MUY AMIGABLE, trata de mantener una conversacion entre tu y el humano:
        - Utiliza unicamente la fuente informativa como la unica verdad, no inventes cosas que no esten en la fuente.
        - La fuente es la siguiente (y esta encapsulada por triple comillas: ```{context}```
        - Del contexto extrae el link y la pagina para tu respuesta.
        - Este es el historial de la conversacion empleada hasta el momento: {chat_history}

        Tarea:
        - Responde o Ejecuta lo siguiente encapsulada por doble comillas: ``{prompt}``
    
        Respuesta formato salto de linea: 
        Respuesta: <respuesta>, \n
        Explicación de la Respuesta: <explica como llegaste a la conclusion de tu respuesta> \n
        Referencia: {{ link:<el link de cloud storage>, pagina: <numero de pagina extraida del contexto>,}}
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

    with st.container():

        if "model" not in st.session_state:
            st.session_state["model"] = model

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []


        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Pregunta algo"):
            st.session_state.chat_history.append({"role": "human_2", "content": prompt})

            with st.chat_message("human_2"):
                st.markdown(prompt)

            with st.chat_message("ai_2.0"):
                full_response = ""
                message_placeholder = st.empty()

                news_source = vertex_search(st.session_state.chat_history[-1]["content"])
                human_last_message = [st.session_state.chat_history[n]["content"] for n,i in enumerate(st.session_state.chat_history) if i["role"] == "human_2"][-1]
                response = google_llm(prompt=human_last_message, context=news_source, chat_history=st.session_state.chat_history , model=st.session_state["model"])

                full_response += (response or "")
                message_placeholder.markdown(full_response + "▌")
            st.session_state.chat_history.append({"role": "ai_2.0", "content": full_response})

    # %%

