from crewai import Task
from textwrap import dedent
import streamlit as st

class SearchAnalysisTask:
    """
    Search Analysis Task
    """
    def search_task(self, agent, query, rag_schema):
        print(f"Action Input: {query}, {rag_schema}")
        context = f"""
        Use the tax_search_tool to gather only description/item and numbers from the
        the following query: {query}, do not forget to pass the query and rag_schema to the tax_search_tool in your input.
        
        The results from tax_search_tool is a combination between spaces and breaklines, so the table looks as follows:
        - The format/schema of your rag output should be description/item //s(withespace) section //n(breakline) amount, for example:
        Gross receipts or sales 1a 
        14,000. 
        - Your first task is to extract from tax_search_tool and understand the structure of that information by doing the following:
        
        Do I need to use a tool? Yes
        Action: text_search_tool
        Action Input: {query}, {rag_schema}
        Response Format: description/item <amount in number>, description/item <amount in number>, ... , etc...  
        
        - If you get another format transform your findings into the following: <item/description_1 value>, <item/description_2> <value_2>, etc.
        If you have multiple items and values, separate them by commas, e.g.:
        
        input: Ordinary business income //s(whitespace) 22\n(breakline) 14,318, rent //s(whitespace) 13 //n(breakline) 350.
        output: Ordinary business income 14,318, rent 350
        
        The third task is pass your results to next task math_task.

        DO NOT change any of the content of the document or add content to it. It is critical
        to your task to only respond with entities and numbers.
        DO NOT resolve any math operation let the other agents to do it.

        """
        
        
        st.markdown(f":green[Agent Task 1]: {context}")
        return Task(description=dedent(context),
      agent=agent
    )
        
    def math_task(self, agent, query):
        context = f"""
        Your first task is to detect math operators needed from the {query} e.g. How much is Gross receipts or sales plus Interes, the operator is +.
        Join your thought with the answer from search_task and pass the operation to math_agent_tool:
        
        Do I need to use a math tool? Yes
        Reasoning: Query; What is the total amount of Gross receipts or sales and repairs and maintenance, response from search_task e.g.; ordinary business income 14,318, rent 350.
        Action: math_agent_tool
        Action Input:  14318-350.
        or Action Input: 14318+350 depending of the context of the query.
        
        Get the math_results from the math_agent_tool and then your response in a verbose way with your findings.
        Rembemer this is your query: {query}.
        Your task is only respond with the summary of what you being asked in the query and your results from the agents if you do not need mathematical operation just answer with your thoughts e.g.:
        
        If you already know the answer or if you do not need to use a tool, return it as
        your Final Answer.
        """
        st.markdown(f":blue[Agent Task 2]: {context}")
        return Task(description=dedent(context),
      agent=agent
    )
        
    def summary_task(self, agent, query):
        context = f"""
        Your only task is to gather information from the other agents to create a summary about your findings with the following information:
        
        Query: {query}
        search_task: response from tax_search_tool agent.
        math_task: result from math_agent_tool.
        
        Explain your response.
        
        If you already know the answer or if you do not need to use a tool, return it as
        your Final Answer.
        If you dont have proper responses from other agents just say you do not know the answer.
        """
        
        st.markdown(f":red[Agent Task 3]: {context}")
        return Task(description=dedent(context),
      agent=agent
    )