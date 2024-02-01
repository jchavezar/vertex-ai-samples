import streamlit as st
from crewai import Crew
from utils.crewai.search_analysis_tasks import SearchAnalysisTask
from utils.crewai.search_analysis_agents import WebsiteAnalysisAgent
from streamlit_extras.colored_header import colored_header

#region Streamlit fields [Optional]
st.set_page_config(
    page_title="Generative AI",
    page_icon="👋",
)

colored_header(
    label="Google Cloud ReAct (LLMs + Vertex Search) 👋",
    description="Using CrewAI to build a search engine for generative AI, other elements used: Google Cloud Storage, Vertex Search, Google Search API, Langchain and Foundational Models (Bison and Gemini)",
    color_name="violet-70",
)

st.image("images/react_vsearch_crewai.png")

#region Model Settings
settings = ["gemini-pro", "text-bison@002", "text-bison-32k@002"]
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


class FinancialCrew:
    def __init__(self):
        self._message = ""
    def run(self, prompt):
        agents = WebsiteAnalysisAgent()
        tasks = SearchAnalysisTask()

        research_analyst_agent = agents.search_analyst()
        research_rag_internal_agent = agents.search_internal()
        research_analyst_task = tasks.search_analysis(research_analyst_agent, query=prompt)
        research_internal_task = tasks.search_financial_internal(research_rag_internal_agent, query=prompt)

        crew = Crew(
            agents=[research_analyst_agent, research_rag_internal_agent],
            tasks=[research_analyst_task],
            verbose=True
        )

        result = crew.kickoff()
        return result



if "crew" not in st.session_state:
    st.session_state["crew"] = ""

st.session_state["crew"] = st.text_input("Ask anything 👇")
if st.session_state["crew"] != "":
        print("jajajaj")
        crew = FinancialCrew()
        result = crew.run(st.session_state["crew"])
        st.info(result.replace("$",""))
        