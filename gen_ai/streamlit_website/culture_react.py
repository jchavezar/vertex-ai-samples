#%%
import re
import httpx
import vertexai
import streamlit as st
from utils import sockcop_vertexai
from vertexai.language_models import TextGenerationModel
from streamlit_extras.colored_header import colored_header
from vertexai.preview.generative_models import GenerativeModel, Part

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "data_store": "countries-and-their-cultur_1706277976842"
}
    

def app(model, parameters):
    st.image("images/react_vsearch_1.png")

    with st.expander("About the Application"):
        st.write("""
                 Content:
                 - For RAG (Vertex Search) the following document was used [Countries and their Culture](https://storage.googleapis.com/vtxdemos-vertex-search-dataset/countries_culture/countries_and_their_cultures.pdf): 

                 Questions to ask?:
                 - Tell me more about the culture in LAOS.
                 - What is the most populated city around the world?
                 - What is Python?

                 Source Code: [github repo](https://github.com/jchavezar/vertex-ai-samples/blob/main/gen_ai/pages/Culture_ReACT%5Bvsearch_unicorn%5D.py)
                 """)

    prompt = """
    You run in a loop of Thought, Action, PAUSE, Observation.
    At the end of the loop you output an Answer
    Use Thought to describe your thoughts about the question you have been asked.
    Use Action to run one of the actions available to you - then return PAUSE.
    Observation will be the result of running those actions.

    Your only available actions are:

    wikipedia:
    e.g. wikipedia: Python
    Returns a summary from searching Wikipedia.

    rag_search (for culture questions):
    e.g. rag_search: Python.
    Search vector database rag for that term.

    summarization:
    e.g. summarization: Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation. Python is dynamically typed and garbage-collected. It supports multiple programming paradigms, including structured, object-oriented and functional programming. Wikipedia
    Returns a summarization for the description.

    -For culture questions prioritize to look at rag_search first for the rest use wikipedia.
    -Do not use any other action which is not wikipedia, rag_search or summarization.
    -If you do not find the answer through the actions just say you do not know it.

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


    with st.expander("How does the prompt looks like?"):
        st.write(prompt)

    _react_settings = ["text-unicorn@001"]
    _summ_settings = ["gemini-pro", "text-bison-32k", "text-bison"]

    #region Model Settings
    with st.sidebar:
        st.info("**Unicorn Start here ↓**", icon="🦄")
        _react_model = st.selectbox("Model for React", _react_settings)
        temperature = st.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], key="r_temp", value=0.2) 
        token_limit = st.select_slider("Token Limit", range(1,1025), key="r_tk_limit", value=1024)
        top_k = st.select_slider("Top-K", range(1, 41), key="r_top_k", value=40)

        _react_parameters =  {
            "temperature": temperature,
            "max_output_tokens": token_limit,
            "top_k": top_k
            }
        st.divider()

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

    client = sockcop_vertexai.Client(variables)
    unicorn_model = TextGenerationModel.from_pretrained(_react_model)

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
            #print(self.messages)
            response = unicorn_model.predict("\n".join(self.messages), **_react_parameters)
            #st.write(response.text)
            print(response.text)
            st.write(response.text)
            return response.text

    #region Action Functions
    def wikipedia(q):
        info = {f"context_{n}":c for n,c in enumerate(httpx.get("https://en.wikipedia.org/w/api.php", params={"action": "query", "list": "search", "srsearch": q, "format": "json"}).json()["query"]["search"]) if n<5}
        print(info)    
        return str(info)

    def rag(q):
        re = client.vertex_search(q)
        st.write(re)
        return re

    def summarization(prompt):
        prompt_template = "Give me a summarization of the following: {}".format(prompt)
        return client.llm2(prompt_template, model, parameters)

    known_actions = {
        "wikipedia": wikipedia,
        "rag_search": rag,
        "summarization": summarization
    }

    action_re = re.compile('^Action: (\w+): (.*)$')
    #endregion

    def query(question, max_turns=5):
        i = 0
        bot = Chatbot(prompt)
        next_prompt = question
        while i < max_turns:
            i += 1
            result = bot("Question: {}".format(next_prompt))
            actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
            if actions:
                # There is an action to run
                action, action_input = actions[0].groups()
                if action not in known_actions:
                    raise Exception("Unknown action: {}: {}".format(action, action_input))
                st.write(" -- running {} {}".format(action, action_input))
                observation = known_actions[action](action_input)
                #st.write("Observation:", observation)
                next_prompt = "Observation: {}".format(observation)
            else:
                return

    p = st.text_input(label="Ask something like 'Tell me more about UK culture'")
    if p != "":
        query(p)
