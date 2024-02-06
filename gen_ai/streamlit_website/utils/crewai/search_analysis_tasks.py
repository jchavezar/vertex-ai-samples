from crewai import Task
from textwrap import dedent

class SearchAnalysisTask:
    """
    Search Analysis Task
    """
    def search_analysis(self, agent, query): 
        return Task(description=dedent(f"""
        Collect any financial information from rag_search/search_internal agent only and the rest from search_analyst/search_tool (internet) :
        
        The following text enclosed by backticks is the query.
        
        ```{query}```
          
        Your final answer MUST be a report that includes a
        comprehensive summary of anything asked.
      """),
      agent=agent
    )
    def search_financial_internal(self, agent, query): 
        return Task(description=dedent(f"""
        Pay special attention to any information about economics/financial in the year asked.
        Use this agent only if you feel the output from the search_analysis task/agent is not reliable.
        
        text:
        ```{query}```
      """),
      agent=agent
    )