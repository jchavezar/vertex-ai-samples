"""Google ADK Framework implementation with native MCP support."""

import os
from typing import Any, AsyncIterator

import logging
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import McpToolset
from google.genai.types import Content, Part
from mcp import StdioServerParameters

from agents.base import AgentFramework, AgentConfig, AgentResponse, AgentType
from models.factory import ModelFactory
from mcp_integration.manager import MCPManager

logger = logging.getLogger(__name__)


class ADKFramework(AgentFramework):
    """Google ADK implementation with native MCP toolset support."""

    framework_name = "adk"

    def __init__(
        self,
        model_factory: ModelFactory,
        mcp_manager: MCPManager,
    ) -> None:
        self.model_factory = model_factory
        self.mcp_manager = mcp_manager
        self._agents: dict[str, Any] = {}
        self._runners: dict[str, Runner] = {}
        self._toolsets: dict[str, list[McpToolset]] = {}  # Track toolsets for cleanup
        self._session_service = InMemorySessionService()

    async def create_agent(self, config: AgentConfig) -> Any:
        """Create an ADK agent with MCP toolsets."""
        provider = self.model_factory.get_provider(config.model_id)
        model_string = provider.get_adk_model_string()

        # Build tools list
        tools = []
        toolsets = []

        # Add MCP server tools using native McpToolset
        for server_id in config.mcp_servers:
            try:
                server_info = self.mcp_manager.registry.get(server_id)
                if not server_info:
                    logger.warning(f"MCP server '{server_id}' not found in registry")
                    continue

                if not server_info.command:
                    logger.warning(f"MCP server '{server_id}' has no command")
                    continue

                # Parse command into executable and args
                cmd_parts = server_info.command.split()
                command = cmd_parts[0]
                args = cmd_parts[1:] if len(cmd_parts) > 1 else []

                # Build environment with system PATH + server-specific env
                env = os.environ.copy()
                if server_info.config and "env" in server_info.config:
                    env.update(server_info.config["env"])

                # Create StdioServerParameters
                server_params = StdioServerParameters(
                    command=command,
                    args=args,
                    env=env,
                )

                # Create McpToolset
                mcp_toolset = McpToolset(
                    connection_params=server_params,
                    tool_name_prefix=f"{server_id}_",
                )

                tools.append(mcp_toolset)
                toolsets.append(mcp_toolset)
                logger.info(f"Added MCP toolset for server: {server_id}")

            except Exception as e:
                logger.error(f"Failed to create MCP toolset for {server_id}: {e}")

        # Store toolsets for cleanup
        self._toolsets[config.agent_id] = toolsets

        # Sanitize name to be a valid identifier (ADK requirement)
        safe_name = config.agent_id.replace("-", "_").replace(" ", "_")
        if not safe_name[0].isalpha() and safe_name[0] != "_":
            safe_name = "_" + safe_name

        # Create appropriate agent type
        if config.agent_type == AgentType.LLM:
            agent = LlmAgent(
                name=safe_name,
                model=model_string,
                instruction=config.system_prompt or "You are a helpful assistant.",
                tools=tools if tools else [],
                description=config.description or config.name,
            )
        elif config.agent_type == AgentType.SEQUENTIAL:
            subagents = [
                self._agents[sa_id]
                for sa_id in config.subagents
                if sa_id in self._agents
            ]
            agent = SequentialAgent(
                name=safe_name,
                sub_agents=subagents,
                description=config.description or config.name,
            )
        elif config.agent_type == AgentType.PARALLEL:
            subagents = [
                self._agents[sa_id]
                for sa_id in config.subagents
                if sa_id in self._agents
            ]
            agent = ParallelAgent(
                name=safe_name,
                sub_agents=subagents,
                description=config.description or config.name,
            )
        elif config.agent_type == AgentType.LOOP:
            subagent = (
                self._agents[config.subagents[0]]
                if config.subagents
                else None
            )
            agent = LoopAgent(
                name=safe_name,
                sub_agent=subagent,
                max_iterations=config.max_iterations,
                description=config.description or config.name,
            )
        elif config.agent_type == AgentType.SUPERVISOR:
            subagent_tools = [
                self._agents[sa_id]
                for sa_id in config.subagents
                if sa_id in self._agents
            ]
            agent = LlmAgent(
                name=safe_name,
                model=model_string,
                instruction=config.system_prompt or "You are a helpful assistant.",
                tools=(tools + subagent_tools) if (tools or subagent_tools) else [],
                description=config.description or config.name,
            )
        else:
            raise ValueError(f"Unsupported agent type: {config.agent_type}")

        # Create runner for this agent
        runner = Runner(
            agent=agent,
            session_service=self._session_service,
            app_name=f"vertex_cowork_{config.agent_id}",
        )

        self._agents[config.agent_id] = agent
        self._runners[config.agent_id] = runner

        logger.info(f"ADK agent created: {config.agent_id} with {len(tools)} MCP toolsets")

        return agent

    async def run(
        self,
        agent_id: str,
        input_message: str,
        session_id: str | None = None,
    ) -> AgentResponse:
        """Run the ADK agent."""
        runner = self._runners.get(agent_id)
        if not runner:
            return AgentResponse(
                content="",
                success=False,
                error=f"Agent '{agent_id}' not found",
            )

        try:
            # Create or get session
            session_id = session_id or f"session_{agent_id}"
            app_name = f"vertex_cowork_{agent_id}"
            user_id = "default_user"

            # Ensure session exists
            existing_session = await self._session_service.get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
            )
            if not existing_session:
                await self._session_service.create_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id,
                )

            # Create Content object for the message
            user_message = Content(
                parts=[Part(text=input_message)],
                role="user",
            )

            # Run the agent
            result = runner.run_async(
                user_id="default_user",
                session_id=session_id,
                new_message=user_message,
            )

            # Collect response from events
            content_parts = []
            tool_calls = []
            intermediate_steps = []

            async for event in result:
                # Extract text from content if present
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            content_parts.append(part.text)
                        if hasattr(part, 'function_call') and part.function_call:
                            tool_calls.append({
                                "name": part.function_call.name,
                                "arguments": dict(part.function_call.args) if part.function_call.args else {},
                            })
                        if hasattr(part, 'function_response') and part.function_response:
                            intermediate_steps.append({
                                "tool": part.function_response.name,
                                "result": str(part.function_response.response),
                            })

            return AgentResponse(
                content="".join(content_parts),
                tool_calls=tool_calls,
                intermediate_steps=intermediate_steps,
                agent_id=agent_id,
                success=True,
            )

        except Exception as e:
            logger.error(f"ADK agent run error for {agent_id}: {e}")
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
        """Stream the ADK agent's response."""
        runner = self._runners.get(agent_id)
        if not runner:
            yield f"Error: Agent '{agent_id}' not found"
            return

        session_id = session_id or f"session_{agent_id}"

        result = await runner.run_async(
            user_id="default_user",
            session_id=session_id,
            new_message=input_message,
        )

        async for event in result:
            if event.type == "text":
                yield event.text

    async def add_tool(self, agent_id: str, tool: Any) -> None:
        """Add a tool to an existing ADK agent."""
        agent = self._agents.get(agent_id)
        if agent and hasattr(agent, "tools"):
            agent.tools.append(tool)

    async def add_mcp_server(self, agent_id: str, server_id: str) -> None:
        """Add MCP server tools to an ADK agent."""
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found")

        server_info = self.mcp_manager.registry.get(server_id)
        if not server_info or not server_info.command:
            raise ValueError(f"MCP server '{server_id}' not found or has no command")

        cmd_parts = server_info.command.split()
        env = os.environ.copy()
        if server_info.config and "env" in server_info.config:
            env.update(server_info.config["env"])

        server_params = StdioServerParameters(
            command=cmd_parts[0],
            args=cmd_parts[1:] if len(cmd_parts) > 1 else [],
            env=env,
        )

        mcp_toolset = McpToolset(
            connection_params=server_params,
            tool_name_prefix=f"{server_id}_",
        )

        if hasattr(agent, "tools"):
            agent.tools.append(mcp_toolset)

        if agent_id not in self._toolsets:
            self._toolsets[agent_id] = []
        self._toolsets[agent_id].append(mcp_toolset)

    async def add_subagent(self, parent_id: str, child_id: str) -> None:
        """Add a subagent to a parent ADK agent."""
        parent = self._agents.get(parent_id)
        child = self._agents.get(child_id)

        if not parent:
            raise ValueError(f"Parent agent '{parent_id}' not found")
        if not child:
            raise ValueError(f"Child agent '{child_id}' not found")

        if hasattr(parent, "tools"):
            parent.tools.append(child)

    def get_agent(self, agent_id: str) -> Any | None:
        """Get an ADK agent by ID."""
        return self._agents.get(agent_id)

    def list_agents(self) -> list[str]:
        """List all ADK agent IDs."""
        return list(self._agents.keys())

    async def cleanup_agent(self, agent_id: str) -> None:
        """Clean up agent resources including MCP toolsets."""
        if agent_id in self._toolsets:
            for toolset in self._toolsets[agent_id]:
                try:
                    await toolset.close()
                except Exception as e:
                    logger.debug(f"Error closing toolset: {e}")
            del self._toolsets[agent_id]

        if agent_id in self._agents:
            del self._agents[agent_id]
        if agent_id in self._runners:
            del self._runners[agent_id]
