from crewai import Task
from textwrap import dedent

class SearchAnalysisTask:
    """
    Search Analysis Task
    """
    def search_analysis(self, agent, query): 
        return Task(description=dedent(f"""
        Collect and summarize recent articles, press
        releases, and market analyses related to {query}.
        Pay special attention to any significant opinions. 
        Also include upcoming  events per country.
        
        For financial and revenue look at internal resources first.
  
        Your final answer MUST be a report that includes a
        comprehensive summary of anything asked.
      """),
      agent=agent
    )