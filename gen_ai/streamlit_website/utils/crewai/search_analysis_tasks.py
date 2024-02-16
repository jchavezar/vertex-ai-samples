from crewai import Task
from textwrap import dedent
import streamlit as st

class SearchAnalysisTask:
    """
    Tax Analysis Task
    """
    def search_analysis(self, agent, query):
      
        context = "Collect any financial tax information from internal_rag tool and everything else from internet tool"
        st.markdown(f":blue[Agent Task 1: {context}]")
        return Task(description=dedent(f"""
        {context}:
        
        The following text enclosed by backticks is the query task.
        
        ```{query}```
          
        Your final answer MUST be a report that includes a
        comprehensive summary of anything asked.
      """),
      agent=agent
    )