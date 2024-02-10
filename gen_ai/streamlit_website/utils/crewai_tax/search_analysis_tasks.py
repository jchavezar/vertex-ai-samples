from crewai import Task
from textwrap import dedent
import streamlit as st

class SearchAnalysisTask:
    """
    Search Analysis Task
    """
    
    def clean_tax(self, agent, query, context):
      temp_prompt = f"""
      You MUST clean_interpret tool always. If math operation is required use calculate tool, Do not try to resolve by yourself.
      
      tools available:
      - clean_interpret
      - calculate
      
      Your main instructions are respond the Query with the following Context:
      
      Context:
      {context}
      
      Query:
      {query}
      
      """
      return Task(description=dedent(temp_prompt),
      agent=agent
    )
  
    def summary_task(self, agent, query):
        general_context = f"""
        Review and synthesize the analyses provided by the
        cleaning_agent_expert and give your Final Answer.
        
        Explain your answer
        
        """
        detailed_context = f"""
        Your final answer MUST be a comprehensive and detailed response.
        """
        #st.markdown(f":red[Agent Task 3]: {general_context}")
        return Task(description=dedent(general_context+detailed_context),
      agent=agent
    )