# ESG Compliance Agent

The following guide will help us to create an Agentic Framework for e
ing sustainable corporate practices.

## Agent Framework Diagram

```mermaid
flowchart LR
    markdown["`Advisory 
    Human
    User`"]
    markdown --> AgentEngine
    AgentEngine --> root_agent(Root ADK Agent)
    root_agent --> rag_agent("`Agent
    with
    Internal Docs
    Access`")
    root_agent --> mcp_agent("`Agent
    with
    MCP Tool
    BigQuery
    `")
    root_agent --> google_search("`Agent
    with
    Google Search
    Tool
    `")
```
## Prework
- Set enviromental variables in your system.

e.g.
```bash
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=vtxdemos
export GOOGLE_CLOUD_LOCATION=us-central1
```

- Install the libraries required.
```bash
pip install google-adk # version currently used: 1.15.1
```

## Step 1: Generate Synthetic Data
Go to [generate_table.py](generate_table.py) and run the script, I used inline run from my IDE (ipython->IntelliJ)
Once the code finishes to run we should be able to see something like this in GCP Console:

![img.png](bigquery_table_image.png)

## Step 2: Use ADK WEB (UI Prototype)
From our terminal on a folder above the current folder "/esg_compliance_agent" we have to run the
following command:

```bash
adk web
```

A window is open like this (select the folder):
![img.png](adk_web_image.png)

And start interacting with the Agent:
![img_1.png](adk_web_interaction_image.png)

Congratulations you have developed this agent framework.
