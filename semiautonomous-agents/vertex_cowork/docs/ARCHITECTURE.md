# Vertex Cowork Architecture

## System Overview

Vertex Cowork is built on a modular architecture that abstracts the underlying agent framework (ADK or LangGraph) while providing a unified API and user interface.

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────────────┐    │
│  │Agent Designer│ │ Chat Interface│ │ MCP Server Manager│    │
│  └──────────────┘ └──────────────┘ └───────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    REST API Layer                    │    │
│  │  /api/models  /api/mcp-servers  /api/agents  /chat   │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Agent Framework Factory                 │    │
│  │  ┌─────────────────┐   ┌─────────────────────────┐  │    │
│  │  │   ADK Framework │   │   LangGraph Framework   │  │    │
│  │  │  ┌───────────┐  │   │  ┌───────────────────┐  │  │    │
│  │  │  │ LlmAgent  │  │   │  │ StateGraph/ReAct  │  │  │    │
│  │  │  │ Sequential│  │   │  │ Supervisor        │  │  │    │
│  │  │  │ Parallel  │  │   │  │ Sequential/Parallel│  │  │    │
│  │  │  │ Loop      │  │   │  └───────────────────┘  │  │    │
│  │  │  └───────────┘  │   │                         │  │    │
│  │  └─────────────────┘   └─────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                               │
│  ┌───────────────┐  ┌─────────────────┐  ┌──────────────┐   │
│  │ Model Factory │  │   MCP Manager   │  │  Registries  │   │
│  │ ┌───────────┐ │  │ ┌─────────────┐ │  │ ┌──────────┐ │   │
│  │ │  Vertex   │ │  │ │ MCP Client  │ │  │ │  Models  │ │   │
│  │ │  Provider │ │  │ │ (stdio/http)│ │  │ │  Agents  │ │   │
│  │ ├───────────┤ │  │ └─────────────┘ │  │ │   MCP    │ │   │
│  │ │  Model    │ │  │                 │  │ └──────────┘ │   │
│  │ │  Garden   │ │  │                 │  │              │   │
│  │ └───────────┘ │  └─────────────────┘  └──────────────┘   │
│  └───────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Vertex AI     │ │   Model Garden  │ │   MCP Servers   │
│   (Gemini)      │ │ (Claude, Llama) │ │ (Tools/Resources)│
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Core Components

### 1. Model Abstraction Layer

```python
class ModelProvider(ABC):
    """Abstract interface for model providers."""
    
    async def generate(self, messages, tools, **kwargs) -> dict
    async def stream(self, messages, tools, **kwargs) -> AsyncIterator[str]
    def get_langchain_model(self) -> Any
    def get_adk_model_string(self) -> str
```

**Providers:**
- `VertexProvider`: Handles Gemini models via Vertex AI
- `ModelGardenProvider`: Handles third-party models (Claude, Llama, Mistral)

### 2. Agent Framework Abstraction

```python
class AgentFramework(ABC):
    """Abstract interface for agent frameworks."""
    
    async def create_agent(self, config: AgentConfig) -> Any
    async def run(self, agent_id, input_message, session_id) -> AgentResponse
    async def stream(self, agent_id, input_message, session_id) -> AsyncIterator[str]
    async def add_tool(self, agent_id, tool) -> None
    async def add_mcp_server(self, agent_id, server_id) -> None
    async def add_subagent(self, parent_id, child_id) -> None
```

**Implementations:**
- `ADKFramework`: Google ADK implementation
- `LangGraphFramework`: LangGraph implementation

### 3. MCP Integration

```python
class MCPClient:
    """Client for MCP server communication."""
    
    async def connect(self) -> None
    async def call_tool(self, tool_name, arguments) -> Any
    async def read_resource(self, uri) -> Any
    def get_tools_for_adk(self) -> list[dict]
    def get_tools_for_langgraph(self) -> list[dict]
```

**Transport Support:**
- `stdio`: Subprocess-based communication
- `sse`: Server-Sent Events
- `http`: HTTP/REST communication

### 4. Registry System

Centralized management of models, agents, and MCP servers:

```python
class ModelRegistry:
    def register(self, model: ModelInfo) -> None
    def get(self, model_id: str) -> ModelInfo | None
    def list_by_provider(self, provider: str) -> list[ModelInfo]

class AgentRegistry:
    def register(self, agent: AgentInfo) -> None
    def get(self, agent_id: str) -> AgentInfo | None
    def list_by_framework(self, framework: str) -> list[AgentInfo]

class MCPServerRegistry:
    def register(self, server: MCPServerInfo) -> None
    def get(self, server_id: str) -> MCPServerInfo | None
```

## Data Flow

### Agent Creation Flow

```
1. User submits agent config via UI/API
                │
                ▼
2. AgentFrameworkFactory selects framework (ADK/LangGraph)
                │
                ▼
3. ModelFactory creates appropriate provider
                │
                ▼
4. MCPManager connects required MCP servers
                │
                ▼
5. Framework creates agent with model + tools
                │
                ▼
6. Agent registered in AgentRegistry
```

### Chat Flow

```
1. User sends message to /api/agents/{id}/chat
                │
                ▼
2. Framework retrieved based on agent's framework type
                │
                ▼
3. framework.run() invoked with message
                │
                ▼
4. Agent processes message:
   - LLM generates response
   - Tools called if needed (MCP or native)
   - Subagents invoked if applicable
                │
                ▼
5. AgentResponse returned to user
```

## Framework Comparison

### Google ADK

```python
# Agent Types
LlmAgent          # LLM-based reasoning
SequentialAgent   # Ordered subagent execution
ParallelAgent     # Concurrent subagent execution
LoopAgent         # Iterative execution

# MCP Integration
McpToolset(connection_params={...})  # Native MCP support

# Session Management
InMemorySessionService()  # Development
VertexAISessionService()  # Production
DatabaseSessionService()  # Custom persistence
```

### LangGraph

```python
# Graph-based agents
StateGraph(AgentState)    # Base graph structure
create_react_agent()      # Prebuilt ReAct agent

# Multi-agent patterns
Supervisor pattern        # Central coordinator
Hierarchical teams        # Nested subgraphs
Parallel execution        # Fan-out/fan-in

# State management
MemorySaver()             # Checkpointing
```

## Evaluation Framework

```python
class AgentEvaluator:
    async def evaluate_case(agent_id, case) -> EvaluationResult
    async def evaluate_agent(agent_id, cases) -> EvaluationReport
    
    def _evaluate_tools(expected, actual, order) -> float
    def _evaluate_content(content, contains, not_contains) -> tuple[float, list]
```

**Evaluation Dimensions:**
1. **Trajectory**: Which tools were called, in what order
2. **Content**: Response quality and accuracy
3. **Performance**: Latency, token usage

## Security Considerations

1. **Model Access**: Controlled via GCP IAM
2. **MCP Servers**: Process isolation, input validation
3. **Tool Execution**: Sandboxed when possible
4. **State Storage**: Encrypted at rest (Cloud SQL, Redis)
5. **API Authentication**: OAuth2/JWT support
