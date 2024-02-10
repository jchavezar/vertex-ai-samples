from textwrap import dedent
from crewai import Agent, Task
from langchain.tools import tool
from langchain_google_vertexai import VertexAI


class sTools:
    
    @tool("clean_interpret")
    def clean_interpret(context: str) -> str:
        """From the context interpret key value pairs.

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
            llm=VertexAI(model="text-unicorn@001", temperature=0.2)
        )
        task = Task(
          agent=agent,
          description=dedent(f"""
        Interpret the Context and get key value pairs even though the data is a mess.
        This is a tax form so is really important to detect items, descriptions, values and field keys like names, addresses, companies, checkboxes, etc...
        
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

    @tool("calculate")
    def calculate(operation):
      """Useful to perform any mathematical calculations, 
      like sum, minus, multiplication, division, etc.
      Transform the input to a mathematical 
      expression, a couple examples are `200*7` or `5000/2*10`
      """
      agent = Agent(
            role="Understanding and Transformation Agent",
            goal="""from `clean_interpret` transform data 
            into something readable to python eval function""",
            backstory="And expert doing math operations",
            llm=VertexAI(model="text-unicorn@001", temperature=0)
        )
      task = Task(
          agent=agent,
          description=dedent("""
          Your Input from `clean_interpret` might look like this: <items/description1>:<value1>\\n<items/description2>:<value2>
          your task is understand the Query and get the mathematical operation required and extract the
          values from the Input and transformt it to make it readable by python eval library:
          
          Example:
          Query: What is the sum between taxes and loses? #tax and loss is an example
          Context from clean_interpret: <key1>:<value1>\\n<key2>:<value2>\\n... e.g. tax:3000\\nloss:5000
          Reasoning: Operator is + and values are 3000 and 5000, so the answer should fit in python eval library function.
          Answer: 3000+5000
          
          """),
          expected_output="3000+5000"
          )
      response = task.execute()
      return eval(response)


"""        Format 1: 
        <key>\n<value>
        
        e.g:
        Total Assets
        15,620
        
        Format 2:
        <key>\\n(breakline))<section>\\n(breakline)<value>
        
        e.g:
        Total Income
        8
        17,850
        
        Format 3:
        <section>\\s<key>\\n<section>\\n<value>

        e.g.
        3 Gross profit. 
        3
        14,000.

        The text should be formated in a key value pair:
        <key1>:<value1>
        <key2>:<value2>
        ...etc"""