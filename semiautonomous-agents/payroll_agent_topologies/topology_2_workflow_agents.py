import os
import time
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv(override=True)
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

from google.adk.agents import Agent
from google.adk import Workflow, Event
from google.adk.runners import Runner
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.sessions import InMemorySessionService
from google.genai import types
from mcp import StdioServerParameters


# Define Routing Schema
class RoutingDecision(BaseModel):
    domain: str = Field(
        description="The primary domain for the query. Options: 'PROFILE', 'EARNINGS', 'EXPENSES', 'ATTENDANCE'"
    )
    original_query: str = Field(description="The exact original user query to be processed by the subagent.")
    explanation: str = Field(description="Brief reason for routing choice")

LAST_ROUTING_DECISION = "None"

def build_workflow_t2():
    print("\n--- Running Topology 2: Workflow with LLM Router and Specialized Agents ---")
    start_time = time.time()

    # Base Server Parameters for Stdio MCP
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "payroll_mcp_server.py"],
        env=os.environ.copy()
    )

    # 1. Specialized Agents configurations with tool filters
    profile_toolset = McpToolset(
        connection_params=StdioConnectionParams(server_params=server_params, timeout=30),
        tool_filter=[
            "get_employee_profile", "update_employee_address", 
            "get_salary_history", "get_company_benefits_summary",
            "get_retirement_contributions_401k", "update_401k_contribution_rate",
            "get_health_insurance_deductions", "update_health_insurance_tier"
        ]
    )
    profile_agent = Agent(
        model="gemini-2.5-flash",
        name="profile_and_benefits_agent",
        instruction="You handle employee profile details, salary histories, general benefits policies, 401(k), and health insurance tiers. The input you receive is the user's query. Use your tools to answer it. Always identify the employee ID from the query. Directly call the appropriate tools without asking for confirmation. Be concise.",
        tools=[profile_toolset]
    )

    earnings_toolset = McpToolset(
        connection_params=StdioConnectionParams(server_params=server_params, timeout=30),
        tool_filter=[
            "get_pay_stubs", "get_ytd_earnings", 
            "calculate_net_pay", "get_payroll_calendar",
            "get_tax_withholding_w4", "update_tax_withholding_w4",
            "get_w2_document", "get_active_deductions"
        ]
    )
    earnings_agent = Agent(
        model="gemini-2.5-flash",
        name="earnings_and_tax_agent",
        instruction="You handle paycheck information, tax W-4 / W-2 settings, active deductions, and pay calendars. The input you receive is the user's query. Use your tools to answer it. Always identify the employee ID from the query. Directly call the appropriate tools without asking for confirmation. Be concise.",
        tools=[earnings_toolset]
    )

    expenses_toolset = McpToolset(
        connection_params=StdioConnectionParams(server_params=server_params, timeout=30),
        tool_filter=[
            "get_direct_deposit_settings", "update_direct_deposit_settings",
            "get_reimbursements", "submit_reimbursement_claim", 
            "add_one_time_bonus"
        ]
    )
    expenses_agent = Agent(
        model="gemini-2.5-flash",
        name="transactions_and_expenses_agent",
        instruction="You handle direct deposit setup, expense claims, reimbursement status, and bonus payouts. The input you receive is the user's query. Use your tools to answer it. Always identify the employee ID from the query. Directly call the appropriate tools without asking for confirmation. Be concise.",
        tools=[expenses_toolset]
    )

    attendance_toolset = McpToolset(
        connection_params=StdioConnectionParams(server_params=server_params, timeout=30),
        tool_filter=[
            "get_accrued_time_off", "request_time_off", "get_time_off_requests"
        ]
    )
    attendance_agent = Agent(
        model="gemini-2.5-flash",
        name="attendance_agent",
        instruction="You handle accrued paid time off (PTO) balances and PTO requests. The input you receive is the user's query. Use your tools to answer it. Always identify the employee ID from the query. Directly call the appropriate tools without asking for confirmation. Be concise.",
        tools=[attendance_toolset]
    )

    # 2. Router Agent (LLM Classifier)
    router_agent = Agent(
        model="gemini-2.5-flash",
        name="payroll_router_agent",
        instruction="""Analyze the incoming user query and classify it into the primary domain.
        Choose exactly one of these:
        - PROFILE: queries about profile, address, salary history, company benefits, 401(k), or health insurance.
        - EARNINGS: queries about pay stubs, W-4 settings, W-2 forms, YTD earnings, or net pay calculations.
        - EXPENSES: queries about direct deposit, submitting reimbursement claims, expense status, or bonuses.
        - ATTENDANCE: queries about PTO balances, requesting time off, or time off request status.""",
        output_schema=RoutingDecision
    )

    # 3. Router Evaluator Node (translates Agent output schema into edge route)
    def route_evaluator(node_input: RoutingDecision):
        global LAST_ROUTING_DECISION
        domain = node_input.domain.upper().strip()
        decision_str = f"{domain} - {node_input.explanation}"
        LAST_ROUTING_DECISION = decision_str
        print(f"[Router Agent Decision]: Domain = {domain} ({node_input.explanation})")
        if domain in ["PROFILE", "EARNINGS", "EXPENSES", "ATTENDANCE"]:
            return Event(route=domain, output=node_input.original_query)
        # Default fallback
        print("Warning: Unknown domain returned. Falling back to PROFILE.")
        return Event(route="PROFILE", output=node_input.original_query)

    # Define Workflow
    workflow = Workflow(
        name="payroll_workflow_router",
        edges=[
            ("START", router_agent, route_evaluator),
            (route_evaluator, {
                "PROFILE": profile_agent,
                "EARNINGS": earnings_agent,
                "EXPENSES": expenses_agent,
                "ATTENDANCE": attendance_agent
            })
        ]
    )
    return workflow

def execute_query_t2(query: str) -> tuple[str, float, str]:
    global LAST_ROUTING_DECISION
    LAST_ROUTING_DECISION = "Pending Classification..."
    
    start_time = time.time()
    workflow = build_workflow_t2()
    
    session_service = InMemorySessionService()
    runner = Runner(
        agent=workflow,
        app_name="payroll_workflow_app",
        session_service=session_service,
        auto_create_session=True
    )

    # Run the workflow
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id="user_123", session_id="session_123", new_message=content)
    
    final_answer = ""
    for event in events:
        if event.is_final_response() and event.content:
            final_answer = event.content.parts[0].text.strip()
    
    elapsed = time.time() - start_time
    return final_answer, elapsed, LAST_ROUTING_DECISION

def run_topology_2():
    print("\n--- Running Topology 2: Workflow with LLM Router and Specialized Agents ---")
    query = "Hi, I am employee EMP101. What is my current accrued PTO balance, and do I have any pending reimbursement claims?"
    print(f"Query: {query}")
    final_answer, elapsed, decision = execute_query_t2(query)
    print(f"[Captured Router Decision]: {decision}")
    print("\nWorkflow Final Response:")
    print(final_answer)
    print(f"\nTime taken: {elapsed:.2f} seconds")

if __name__ == "__main__":
    run_topology_2()
