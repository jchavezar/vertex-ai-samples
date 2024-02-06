from textwrap import dedent
from typing import List

from langchain.tools import Tool
from pydantic import BaseModel, Field

from crewai.agent import Agent
from crewai.task import Task


class TaskTools(BaseModel):
	"""Default tools around task results retrieval"""

	tasks: List[Task] = Field(description="List of tasks.")

	def tools(self):
		return [
			Tool.from_function(
				func=self.retrieve_outcome,
				name="Retrieve previous tasks outcome",
				description=dedent(f"""Useful to retrieve the outcome of a
				previously completed task.
				The input to this tool should be one of the available task.
				Available tasks:
				{self.__format_tasks()}
				"""
				),
			),
		]

	def retrieve_outcome(self, description):
			"""Useful to retrieve the outcome of a completed task."""
			if not description:
				return "\nError using tool. Missing the task input."

			if description not in [task.output.summary for task in self.tasks]:
				return dedent(f"""\
						Error using tool. Task not found, use one of the available tasks.
						Available tasks:
						{self.__format_tasks()}
					""")

			task = [task for task in self.tasks if task.output.summary == description][0]
			return task.output.result

	def __format_tasks(self):
			"""Format tasks dict to string."""
			tasks = [task.output for task in self.tasks if task.output]
			print("##########################")
			print(tasks)
			print("##########################")
			return "\n".join([f"- {task.summary}" for task in tasks])