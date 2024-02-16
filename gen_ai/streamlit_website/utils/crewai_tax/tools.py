import streamlit as st
from textwrap import dedent
from crewai import Agent, Task
from langchain.tools import tool, Tool
from langchain_google_vertexai import VertexAI
from langchain.chains.llm_math.base import LLMMathChain
#from langchain_community.chat_models.vertexai import ChatVertexAI
#from langchain_google_vertexai import VertexAI


class sTools:
    
    #region Context Clean Tool
    @tool("clean_interpret")
    def clean_interpret(context: str) -> str:
        """From the context extract key value pairs.

        Args:
            context (str): unstructured data with names, sections number, items/description, values, etc.

        Returns:
            str: items/description values or entities names.
        """
        
        agent = Agent(
            role="Data Cleaning Expert",
            goal=dedent("Get keys like names, items, descriptions, numbers and values"),
            backstory=dedent("""You are the best of the best detecting patterns in data, the context is a mess but you
            are a very intelligent agent to interpret information, data are tax forms so is important not loss any detail.
            """),
            llm=VertexAI(model_name="text-unicorn@001", temperature=0)
        )
        task = Task(
          agent=agent,
          description=dedent(f"""
        Interpret the Context and get key value pairs even though the data is a mess.
        This is a tax form therefore it is really important to detect items, descriptions, values and field keys like names, addresses, companies, checkboxes, etc...
        If you have both responses in checkboxes checked, just respond with 'there is no clear selection.'
        Sometimes you have text following by text in a breakline, for those cases your key:value is <text>:<text>.
        Sometimes you can also have text following by text but the next 2 breaklines are numbers, for those cases you can skip the second line text and extract the values.
        
        General Rules:
        - 1 digit or 1 digit and a character indicates a section, drop these from your output.
        - Values can be money, or even text.
        - checkboxes are important, if you get 1 check represent it as <key>:True.
        
        Context:
        {context}
        
        
        """),
        expected_output=dedent("""
        <key1>:<value1>
        <key2>:<value2>
        <key3>:<value3>
        ... etc
        
        """)
 
      )
        response = task.execute()
        return response
    #endreigon
      
    #region Math Tool
    math_model = "text-unicorn@001"
    #st.markdown(f":blue[Model Used by Clean Agent for Math Operations:] {math_model}")
    math_llm = VertexAI(model_name=math_model, temperature=0)
    llm_math_chain = LLMMathChain.from_llm(llm=math_llm)
    math_tool = Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful when you need to answer questions about math"
    )
    #endregion