#%%
import streamlit as st
from crewai import Crew
from search_analysis_agents import WebsiteAnalysisAgent
from search_analysis_tasks import SearchAnalysisTask


class FinancialCrew:
    def run(self, prompt):
        agents = WebsiteAnalysisAgent()
        tasks = SearchAnalysisTask()

        research_analyst_agent = agents.search_analyst()
        research_rag_internal_agent = agents.search_internal()
        research_analyst_task = tasks.search_analysis(research_analyst_agent, query=prompt)
        research_internal_task = tasks.search_financial_internal(research_rag_internal_agent, query=prompt)

        crew = Crew(
            agents=[research_analyst_agent, research_rag_internal_agent],
            tasks=[research_analyst_task, research_internal_task],
            verbose=True
        )

        result = crew.kickoff()
        return result

if __name__ == "__main__":
    with st.container():
        input = st.text_input("write something...")
        if input != "":
            crew = FinancialCrew()
            result = crew.run(input)
    with st.container():
        if input != "":
            st.info(result.replace("$",""))
        