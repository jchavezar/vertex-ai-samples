import inspect
from google.adk import Agent
from google.adk.agents.sequential_agent import SequentialAgent

print("Agent.run_async signature:")
print(inspect.signature(Agent.run_async))

print("\nSequentialAgent.run_async signature:")
print(inspect.signature(SequentialAgent.run_async))
