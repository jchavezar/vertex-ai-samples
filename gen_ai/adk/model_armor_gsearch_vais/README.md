# Model Armor Guardrail Implementations for GenAI Agents

This project demonstrates two distinct approaches for integrating "Model Armor" as a safety guardrail within a Generative AI agent built using the Agent Development Kit (ADK). The primary goal is to detect and handle Personally Identifiable Information (PII) in user queries before they are processed by other tools or the core model.

The two subdirectories showcase different methods for implementing these PII guardrails.

---

## 1. `as_tool_function` (Soft Guardrail)

This directory contains an agent that implements the PII check as a standard tool that the agent can choose to call.

*   **Mechanism**: Model Armor is wrapped as a tool. Through careful prompt engineering, the agent is instructed to prioritize calling this tool first to scan for PII.
*   **User Interaction**: If the Model Armor tool detects PII, the agent's logic is designed to ask the user for confirmation before proceeding with other tools, such as Google Search. This gives the user explicit control over their data.
*   **Classification**: This is considered a **"soft guardrail"** because its execution relies on the agent's programming and ability to follow the prompt's instructions, rather than a hard-coded, pre-emptive check.

---

## 2. `before_model_callback` (Hard Guardrail)

This directory demonstrates a more robust, pre-emptive approach using a callback function that intercepts the query.

*   **Mechanism**: This implementation leverages the `before_model_callback` feature of the ADK. This function is guaranteed to execute and inspect the user's query *before* it is sent to the main agent model.
*   **User Interaction**: The callback function itself uses Model Armor to inspect the query. If PII is found, the callback logic interacts directly with the end-user to ask for consent to continue. The main agent is only invoked after receiving a positive confirmation.
*   **Classification**: This is considered a **"hard guardrail"** because it enforces the PII check at an infrastructure level, before the agent's core logic begins processing the request. This check cannot be bypassed by the agent's reasoning process.