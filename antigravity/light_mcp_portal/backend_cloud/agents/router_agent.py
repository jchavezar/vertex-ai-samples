import os
from typing import Optional, List
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.genai import types

# 1. Define the Router Result Schema
class RouterResult(BaseModel):
    intent: str = Field(description="The intent of the user. Must be one of: 'SERVICENOW', 'SEARCH', 'CANCEL'")
    reasoning: str = Field(description="The reasoning behind the classification")

def get_router_agent(model_name: str = "gemini-3-flash-preview") -> LlmAgent:
    """
    Returns a State-less Router Agent that classifies user intent into:
    - SERVICENOW: Asking about incidents, tickets, or ServiceNow actions.
    - SEARCH: General questions, finding information, or documents.
    - CANCEL: The user wants to stop or cancel.
    """
    instruction = """
    You are a State-less Router Agent for a Lightweight Portal. Your ONLY job is to classify the user's input into one of three categories:
    
    1. **SERVICENOW**: If the user is asking to create, list, find, update, or check any IT incident, ticket, or ServiceNow-related item.
    2. **SEARCH**: If the user is asking general questions, looking for information, policies, documents, or anything that requires a knowledge base search.
    3. **CANCEL**: If the user wants to cancel the current operation or reset the conversation.

    You MUST output your answer matching the required JSON schema.
    Reasoning should be brief.
    """

    agent = LlmAgent(
        name="router_agent",
        model=model_name,
        instruction=instruction,
        output_schema=RouterResult,
        output_key="router_classification"
    )
    
    return agent
