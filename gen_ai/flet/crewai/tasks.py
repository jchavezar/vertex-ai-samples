from crewai import Task
from textwrap import dedent


class AnalysisTasks:
    def research(self, agent, query):
        return Task(
            description=dedent(f"""
            Collect and summarize recent articles related to the following
            query: {query}.
            Pay special attention to any significant events and historical information.
      
            Your final answer MUST be a report that includes a
            comprehensive summary of the latest news, any notable
            shifts related to the {query}.
      
            Make sure to use the most recent data as possible.
            """),
            expected_output=dedent("""A list of summaries about your findings"""),
            agent=agent
        )