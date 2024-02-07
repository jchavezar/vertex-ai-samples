from crewai import Task
from textwrap import dedent
import streamlit as st

class SearchAnalysisTask:
    """
    Search Analysis Task
    """
    def search_analysis(self, agent, query):
      
        context = "Collect any financial information from 'Financial Internal Data Analyst' agent only and the rest from the Internet Scraping Agent (internet)"
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