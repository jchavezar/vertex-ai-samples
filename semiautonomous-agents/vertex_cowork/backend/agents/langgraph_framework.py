"""LangGraph Framework implementation."""

from typing import Any, AsyncIterator, Annotated, TypedDict
import operator

import logging
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool as langchain_tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from agents.base import AgentFramework, AgentConfig, AgentResponse, AgentType
from models.factory import ModelFactory
from mcp_integration.manager import MCPManager

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State schema for LangGraph agents."""

    messages: Annotated[list[BaseMessage], add_messages]
    intermediate_steps: list[dict[str, Any]]
    current_agent: str


class LangGraphFramework(AgentFramework):
    """LangGraph implementation of the agent framework."""

    framework_name = "langgraph"

    def __init__(
        self,
        model_factory: ModelFactory,
        mcp_manager: MCPManager,
    ) -> None:
        self.model_factory = model_factory
        self.mcp_manager = mcp_manager
        self._agents: dict[str, Any] = {}
        self._graphs: dict[str, StateGraph] = {}
        self._compiled_graphs: dict[str, Any] = {}
        self._configs: dict[str, AgentConfig] = {}
        self._memory = MemorySaver()

    async def create_agent(self, config: AgentConfig) -> Any:
        """Create a LangGraph agent."""
        provider = self.model_factory.get_provider(config.model_id)
        llm = provider.get_langchain_model()

        # Build tools list
        tools = []
        for tool_name in config.tools:
            # Custom tools would be loaded from a tool registry
            pass

        # Add MCP server tools as LangChain tools
        for server_id in config.mcp_servers:
            try:
                client = await self.mcp_manager.connect_server(server_id)
                mcp_tools = self._create_mcp_tools(server_id, client)
                tools.extend(mcp_tools)
            except Exception as e:
                logger.warning(f"Failed to add MCP server {server_id}: {e}")

        # Create appropriate graph type
        if config.agent_type == AgentType.LLM:
            graph = self._create_react_agent(config, llm, tools)
        elif config.agent_type == AgentType.SUPERVISOR:
            graph = self._create_supervisor_agent(config, llm, tools)
        elif config.agent_type == AgentType.SEQUENTIAL:
            graph = self._create_sequential_agent(config, llm)
        elif config.agent_type == AgentType.PARALLEL:
            graph = self._create_parallel_agent(config, llm)
        else:
            # Default to ReAct agent
            graph = self._create_react_agent(config, llm, tools)

        # Compile the graph
        compiled = graph.compile(checkpointer=self._memory)

        self._agents[config.agent_id] = compiled
        self._graphs[config.agent_id] = graph
        self._compiled_graphs[config.agent_id] = compiled
        self._configs[config.agent_id] = config

        logger.info(f"LangGraph agent created: {config.agent_id}")

        return compiled

    def _create_react_agent(
        self,
        config: AgentConfig,
        llm: Any,
        tools: list[Any],
    ) -> StateGraph:
        """Create a ReAct-style agent graph."""
        # Use LangGraph's prebuilt ReAct agent
        if tools:
            llm_with_tools = llm.bind_tools(tools)
        else:
            llm_with_tools = llm

        # Build the graph
        graph = StateGraph(AgentState)

        # Define nodes
        async def agent_node(state: AgentState) -> dict[str, Any]:
            """Agent reasoning node."""
            messages = state["messages"]
            if config.system_prompt:
                messages = [SystemMessage(content=config.system_prompt)] + messages

            response = await llm_with_tools.ainvoke(messages)
            return {"messages": [response]}

        async def tool_node(state: AgentState) -> dict[str, Any]:
            """Tool execution node."""
            last_message = state["messages"][-1]
            if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
                return {"messages": []}

            tool_results = []
            for tool_call in last_message.tool_calls:
                # Execute tool
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # Find and execute the tool
                for t in tools:
                    if t.name == tool_name:
                        result = await t.ainvoke(tool_args)
                        tool_results.append({
                            "role": "tool",
                            "name": tool_name,
                            "content": str(result),
                            "tool_call_id": tool_call.get("id", ""),
                        })
                        break

            return {"messages": tool_results}

        def should_continue(state: AgentState) -> str:
            """Determine if we should continue to tools or end."""
            last_message = state["messages"][-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            return END

        # Add nodes
        graph.add_node("agent", agent_node)
        if tools:
            graph.add_node("tools", tool_node)

        # Add edges
        graph.set_entry_point("agent")
        if tools:
            graph.add_conditional_edges(
                "agent",
                should_continue,
                {"tools": "tools", END: END},
            )
            graph.add_edge("tools", "agent")
        else:
            graph.add_edge("agent", END)

        return graph

    def _create_supervisor_agent(
        self,
        config: AgentConfig,
        llm: Any,
        tools: list[Any],
    ) -> StateGraph:
        """Create a supervisor agent that orchestrates subagents."""
        graph = StateGraph(AgentState)

        # Get subagent graphs
        subagent_names = []
        for sa_id in config.subagents:
            if sa_id in self._compiled_graphs:
                subagent_names.append(sa_id)

        async def supervisor_node(state: AgentState) -> dict[str, Any]:
            """Supervisor decides which subagent to call."""
            system_prompt = f"""You are a supervisor managing these agents: {subagent_names}.
            Given the user request, decide which agent should handle it.
            Respond with the agent name or 'FINISH' if done.

            {config.system_prompt}"""

            messages = [SystemMessage(content=system_prompt)] + state["messages"]
            response = await llm.ainvoke(messages)
            return {"messages": [response], "current_agent": response.content.strip()}

        async def subagent_node(state: AgentState) -> dict[str, Any]:
            """Execute the selected subagent."""
            current = state.get("current_agent", "")
            if current in self._compiled_graphs:
                subgraph = self._compiled_graphs[current]
                result = await subgraph.ainvoke(
                    {"messages": state["messages"]},
                    config={"configurable": {"thread_id": "subagent"}},
                )
                return {"messages": result["messages"]}
            return {"messages": []}

        def route_to_agent(state: AgentState) -> str:
            """Route to appropriate agent or end."""
            current = state.get("current_agent", "")
            if current.upper() == "FINISH" or not current:
                return END
            if current in subagent_names:
                return "subagent"
            return END

        # Add nodes
        graph.add_node("supervisor", supervisor_node)
        graph.add_node("subagent", subagent_node)

        # Add edges
        graph.set_entry_point("supervisor")
        graph.add_conditional_edges(
            "supervisor",
            route_to_agent,
            {**{sa: "subagent" for sa in subagent_names}, END: END},
        )
        graph.add_edge("subagent", "supervisor")

        return graph

    def _create_sequential_agent(
        self,
        config: AgentConfig,
        llm: Any,
    ) -> StateGraph:
        """Create a sequential agent that runs subagents in order."""
        graph = StateGraph(AgentState)

        # Add each subagent as a node
        for i, sa_id in enumerate(config.subagents):
            if sa_id not in self._compiled_graphs:
                continue

            async def subagent_node(
                state: AgentState,
                subagent_id: str = sa_id,
            ) -> dict[str, Any]:
                subgraph = self._compiled_graphs[subagent_id]
                result = await subgraph.ainvoke(
                    {"messages": state["messages"]},
                    config={"configurable": {"thread_id": f"seq_{subagent_id}"}},
                )
                return {"messages": result["messages"]}

            graph.add_node(sa_id, subagent_node)

        # Chain subagents sequentially
        for i, sa_id in enumerate(config.subagents[:-1]):
            next_id = config.subagents[i + 1]
            if i == 0:
                graph.set_entry_point(sa_id)
            graph.add_edge(sa_id, next_id)

        # End after last subagent
        if config.subagents:
            graph.add_edge(config.subagents[-1], END)

        return graph

    def _create_parallel_agent(
        self,
        config: AgentConfig,
        llm: Any,
    ) -> StateGraph:
        """Create a parallel agent that runs subagents concurrently."""
        import asyncio

        graph = StateGraph(AgentState)

        async def parallel_node(state: AgentState) -> dict[str, Any]:
            """Run all subagents in parallel."""
            tasks = []
            for sa_id in config.subagents:
                if sa_id in self._compiled_graphs:
                    subgraph = self._compiled_graphs[sa_id]
                    task = subgraph.ainvoke(
                        {"messages": state["messages"]},
                        config={"configurable": {"thread_id": f"par_{sa_id}"}},
                    )
                    tasks.append(task)

            results = await asyncio.gather(*tasks)

            # Aggregate messages from all subagents
            all_messages = []
            for result in results:
                all_messages.extend(result.get("messages", []))

            return {"messages": all_messages}

        graph.add_node("parallel", parallel_node)
        graph.set_entry_point("parallel")
        graph.add_edge("parallel", END)

        return graph

    def _create_mcp_tools(self, server_id: str, client: Any) -> list[Any]:
        """Create LangChain tools from MCP server tools."""
        tools = []
        mcp_manager = self.mcp_manager

        for mcp_tool in client.get_tools():
            # Create a closure to capture tool name
            def create_tool_func(tool_name: str, srv_id: str):
                async def tool_func(**kwargs: Any) -> str:
                    result = await mcp_manager.call_tool(srv_id, tool_name, kwargs)
                    return str(result)

                tool_func.__name__ = tool_name
                tool_func.__doc__ = mcp_tool.description
                return tool_func

            func = create_tool_func(mcp_tool.name, server_id)
            lc_tool = langchain_tool(func)
            tools.append(lc_tool)

        return tools

    async def run(
        self,
        agent_id: str,
        input_message: str,
        session_id: str | None = None,
    ) -> AgentResponse:
        """Run the LangGraph agent."""
        compiled = self._compiled_graphs.get(agent_id)
        if not compiled:
            return AgentResponse(
                content="",
                success=False,
                error=f"Agent '{agent_id}' not found",
            )

        try:
            thread_id = session_id or f"thread_{agent_id}"

            result = await compiled.ainvoke(
                {"messages": [HumanMessage(content=input_message)]},
                config={"configurable": {"thread_id": thread_id}},
            )

            # Extract final response
            messages = result.get("messages", [])
            final_content = ""
            tool_calls = []

            for msg in messages:
                if isinstance(msg, AIMessage):
                    final_content = msg.content
                    if hasattr(msg, "tool_calls"):
                        tool_calls.extend(msg.tool_calls)

            return AgentResponse(
                content=final_content,
                tool_calls=tool_calls,
                intermediate_steps=result.get("intermediate_steps", []),
                agent_id=agent_id,
                success=True,
            )

        except Exception as e:
            logger.error(f"LangGraph agent run error for {agent_id}: {e}")
            return AgentResponse(
                content="",
                success=False,
                error=str(e),
                agent_id=agent_id,
            )

    async def stream(
        self,
        agent_id: str,
        input_message: str,
        session_id: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream the LangGraph agent's response."""
        compiled = self._compiled_graphs.get(agent_id)
        if not compiled:
            yield f"Error: Agent '{agent_id}' not found"
            return

        thread_id = session_id or f"thread_{agent_id}"

        async for event in compiled.astream_events(
            {"messages": [HumanMessage(content=input_message)]},
            config={"configurable": {"thread_id": thread_id}},
            version="v1",
        ):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content") and chunk.content:
                    yield chunk.content

    async def add_tool(self, agent_id: str, tool: Any) -> None:
        """Add a tool to an existing LangGraph agent."""
        config = self._configs.get(agent_id)
        if config:
            config.tools.append(tool)
            # Rebuild the agent with new tools
            await self.create_agent(config)

    async def add_mcp_server(self, agent_id: str, server_id: str) -> None:
        """Add MCP server tools to a LangGraph agent."""
        config = self._configs.get(agent_id)
        if config:
            config.mcp_servers.append(server_id)
            # Rebuild the agent with new MCP server
            await self.create_agent(config)

    async def add_subagent(self, parent_id: str, child_id: str) -> None:
        """Add a subagent to a parent LangGraph agent."""
        config = self._configs.get(parent_id)
        if config:
            config.subagents.append(child_id)
            # Rebuild the agent with new subagent
            await self.create_agent(config)

    def get_agent(self, agent_id: str) -> Any | None:
        """Get a LangGraph agent by ID."""
        return self._compiled_graphs.get(agent_id)

    def list_agents(self) -> list[str]:
        """List all LangGraph agent IDs."""
        return list(self._compiled_graphs.keys())
