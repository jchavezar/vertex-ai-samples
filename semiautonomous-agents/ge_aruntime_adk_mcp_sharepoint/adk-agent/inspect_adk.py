import vertexai
from vertexai import agent_engines
import inspect

print("Attributes of vertexai.agent_engines:")
for name in dir(agent_engines):
    if not name.startswith("_"):
        print(name)

print("\nAttributes of vertexai.Client:")
client = vertexai.Client(project="vtxdemos", location="us-central1")
for name in dir(client):
    if not name.startswith("_"):
        print(name)

print("\nAttributes of client.agent_engines:")
for name in dir(client.agent_engines):
    if not name.startswith("_"):
        print(name)
