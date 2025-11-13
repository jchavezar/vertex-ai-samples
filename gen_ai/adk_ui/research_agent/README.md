# `research_agent` - Iterative Research System

This directory contains the configuration files for a sophisticated multi-agent system meticulously designed for iterative research. This system orchestrates specialized agents to intelligently refine search queries, efficiently execute searches, and synthesize valuable information, all seamlessly coordinated within a dynamic research loop.

## ✨ Iterative Research Flow: Unveiling the Research Process ✨

Dive into the core mechanics of this multi-agent system with this flowchart, illustrating the high-level process from a user's initial research topic to the final delivery of results:

```mermaid
graph TD
    A[User Provides Research Topic] --> B[Research Coordinator];
    B --> C{Research Loop (max 3 iterations)};
    C -- Iteration Start --> D[Query Refinement Agent];
    D -- Refined Query --> E[Search Execution Agent];
    E -- Search Results --> D;
    D -- Research Complete / No Further Productive Searches --> F[Exit Loop];
    F --> G[Research Coordinator Delivers Results];
```

## 🚀 Getting Started: Embarking on Your Research Journey 🚀

To effectively initiate and manage a research task using this powerful system, follow these key steps:

1.  **Start the Research Coordinator**: The `root_agent.yaml` file is the blueprint for the `research_coordinator` agent. This agent serves as the primary entry point, ready to receive and process your research topics.
2.  **Provide a Research Topic**: Engage with the `research_coordinator` by clearly articulating your specific research topic or question. This will set the entire iterative process in motion.
3.  **Observe the Research Loop**: Once a topic is provided, the `research_coordinator` intelligently delegates the task to the `research_loop` agent (defined in `research_loop.yaml`). This loop will then autonomously and iteratively refine queries and execute searches, driving the research forward.
4.  **Dependencies**: It is crucial to ensure that the `google_search` tool (which is typically defined and made available in your environment, similar to how tools are managed in the `mcp_multiagent_ui/tools` directory) is correctly configured. This is essential for the `search_execution_agent` to perform its functions effectively.

## 🧠 Agent Overview: The Specialists Driving Your Research 🧠

Here's a detailed look at the specialized agents configured within this directory, each playing a vital role in the iterative research process:

*   **`query_refinement_agent.yaml`**: Configures the highly intelligent `Query Refinement Agent`. This agent meticulously analyzes previous search results, dynamically refines search queries for subsequent iterations, and critically determines when the research objective has been comprehensively met or if no further productive searches can be performed. Upon such a determination, it signals the `research_loop` to gracefully terminate.
*   **`research_loop.yaml`**: Defines the core `Research Loop` agent. As a `LoopAgent`, it iteratively and strategically orchestrates the `Query Refinement Agent` and the `Search Execution Agent` for a predefined maximum number of iterations (e.g., 3, as explicitly configured). Its paramount role is to drive the entire iterative research process with precision and efficiency.
*   **`root_agent.yaml`**: Configures the overarching `Research Coordinator` agent. This top-level agent is singularly responsible for accepting research topics directly from the user, initiating the intricate iterative research process by delegating to the `Research Loop`, and ultimately, meticulously delivering the synthesized and comprehensive research results back to the user.
*   **`search_execution_agent.yaml`**: Configures the efficient `Search Execution Agent`. This agent's primary function is to take a refined search query, execute it with speed and accuracy using the `google_search` tool, and then expertly extract all relevant information and key insights directly from the search results.
