import streamlit as st
from crewai import Crew
from utils.links_references import *
from utils.crewai.search_analysis_tasks import SearchAnalysisTask
from utils.crewai.search_analysis_agents import WebsiteAnalysisAgent
from streamlit_extras.colored_header import colored_header

def app(model, parameters):
    st.image("images/react_vsearch_crewai.png")
    st.markdown(f""" :green[repo:] [![Repo]({github_icon})]({crewai_qa})""")
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


    class FinancialCrew:
        def __init__(self):
            self._message = ""
        def run(self, prompt):
            agents = WebsiteAnalysisAgent()
            tasks = SearchAnalysisTask()

            research_analyst_agent = agents.search_analyst(model, parameters)
            research_rag_internal_agent = agents.search_internal()
            research_analyst_task = tasks.search_analysis(research_analyst_agent, query=prompt)

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
            crew = FinancialCrew()
            result = crew.run(st.session_state["crew"])
            st.info(result)
