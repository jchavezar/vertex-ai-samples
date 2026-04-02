# Vertex Cowork

Enterprise Agent Platform with Multi-Model Support, MCP Connectivity, and Framework Flexibility (ADK + LangGraph)

## Overview

Vertex Cowork is a next-generation enterprise agent platform that provides:

- **Multi-Model Support**: Select from Vertex AI managed models (Gemini) or Model Garden (Claude, Llama, Mistral)
- **MCP Server Connectivity**: Connect to any Model Context Protocol server for tool integration
- **Agent Designer**: Visual interface for creating agents, subagents, and multi-agent systems
- **Framework Flexibility**: Choose between Google ADK or LangGraph to build your agents
- **Evaluation Framework**: Built-in testing and evaluation for agent behavior

## Architecture

```
vertex_cowork/
├── backend/
│   ├── core/              # Configuration, registries
│   ├── models/            # Model provider abstraction
│   ├── mcp/               # MCP server management
│   ├── agents/            # Agent framework abstraction (ADK/LangGraph)
│   ├── evaluation/        # Agent evaluation framework
│   └── main.py            # FastAPI application
├── frontend/
│   └── src/
│       ├── components/    # React components
│       ├── hooks/         # Custom hooks
│       ├── types/         # TypeScript types
│       └── utils/         # API client
├── tests/                 # Unit and integration tests
└── docs/                  # Documentation
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Google Cloud Project with Vertex AI enabled
- `gcloud` CLI authenticated

### Setup

```bash
# Clone and navigate
cd semiautonomous-agents/vertex_cowork

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export AGENT_NEXUS_GCP_PROJECT_ID="your-project-id"
export AGENT_NEXUS_GCP_LOCATION="us-central1"

# Start backend
python main.py

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

## Features

### 1. Multi-Model Selection

Choose from multiple model providers:

| Provider | Models | Best For |
|----------|--------|----------|
| Vertex AI | Gemini 2.0 Flash, Gemini 2.0 Pro, Gemini 2.5 Pro Preview | Native GCP integration, fast inference |
| Model Garden | Claude 3.5 Sonnet, Claude 3 Opus, Llama 3.1 405B, Mistral Large 2 | Model diversity, specific capabilities |

### 2. MCP Server Integration

Connect to any MCP-compatible server:

```python
# Register an MCP server
POST /api/mcp-servers
{
  "server_id": "filesystem",
  "name": "Filesystem Server",
  "transport": "stdio",
  "command": "npx -y @modelcontextprotocol/server-filesystem /path/to/dir"
}

# Connect to the server
POST /api/mcp-servers/filesystem/connect
```

### 3. Agent Designer

Create agents with the visual designer or API:

```python
# Create an LLM agent
POST /api/agents
{
  "agent_id": "research-agent",
  "name": "Research Agent",
  "model_id": "gemini-2.0-flash",
  "framework": "adk",  # or "langgraph"
  "agent_type": "llm",
  "system_prompt": "You are a research assistant...",
  "mcp_servers": ["filesystem", "web-search"]
}
```

### 4. Framework Comparison

| Feature | Google ADK | LangGraph |
|---------|------------|-----------|
| MCP Support | Native McpToolset | Via LangChain tools |
| Multi-Agent | SequentialAgent, ParallelAgent, LoopAgent | StateGraph, Supervisor pattern |
| State Management | SessionService, InMemory/DB | MemorySaver, Checkpointer |
| Deployment | Vertex AI Agent Engine | Cloud Run, custom |
| Best For | GCP-native, Gemini-optimized | Complex workflows, LangChain ecosystem |

### 5. Agent Types

- **LLM Agent**: Reasoning agent powered by an LLM
- **Supervisor**: Orchestrates multiple subagents
- **Sequential**: Runs subagents in order
- **Parallel**: Runs subagents concurrently
- **Loop**: Iterative execution agent

## API Reference

### Models

```
GET  /api/models              # List all models
GET  /api/models?provider=X   # Filter by provider
GET  /api/models/{model_id}   # Get specific model
```

### MCP Servers

```
GET  /api/mcp-servers                    # List servers
POST /api/mcp-servers                    # Register server
POST /api/mcp-servers/{id}/connect       # Connect
POST /api/mcp-servers/{id}/disconnect    # Disconnect
```

### Agents

```
GET    /api/agents              # List agents
POST   /api/agents              # Create agent
GET    /api/agents/{id}         # Get agent
DELETE /api/agents/{id}         # Delete agent
POST   /api/agents/{id}/chat    # Chat with agent
```

### Frameworks

```
GET /api/frameworks             # List available frameworks
```

## Evaluation

Test agent behavior with the evaluation framework:

```python
from evaluation.evaluator import AgentEvaluator, EvaluationCase

evaluator = AgentEvaluator(framework)

case = EvaluationCase(
    case_id="search-test",
    description="Test search functionality",
    input_message="Search for Python tutorials",
    expected_tools=["search"],
    expected_content_contains=["python", "tutorial"],
)

result = await evaluator.evaluate_case("my-agent", case)
print(f"Passed: {result.passed}, Score: {result.score}")
```

## Best Practices

### Agent Design

1. **Single Responsibility**: Each agent should have a focused purpose
2. **Tool Selection**: Only include tools the agent actually needs
3. **System Prompts**: Be specific about the agent's role and constraints
4. **Temperature**: Use lower values (0.1-0.3) for deterministic tasks

### Multi-Agent Systems

1. **Supervisor Pattern**: Use for complex orchestration with dynamic routing
2. **Sequential Pattern**: Use for pipeline-style processing
3. **Parallel Pattern**: Use for independent subtasks that can run concurrently

### MCP Server Security

1. **Limit Commands**: Only expose necessary tools
2. **Validate Inputs**: Sanitize tool arguments before execution
3. **Monitor Usage**: Log all tool calls for audit

### Evaluation

1. **Golden Datasets**: Create comprehensive test cases
2. **Tool Trajectories**: Verify expected tool sequences
3. **Content Validation**: Check for required and forbidden content
4. **Regression Testing**: Run evaluations on every change

## Deployment

### Local Development

```bash
# Backend
cd backend && python main.py

# Frontend
cd frontend && npm run dev
```

### Docker

```bash
docker-compose up -d
```

### Cloud Run

```bash
# Build and deploy backend
gcloud run deploy agent-nexus-api \
  --source ./backend \
  --region us-central1 \
  --allow-unauthenticated

# Build and deploy frontend
gcloud run deploy agent-nexus-ui \
  --source ./frontend \
  --region us-central1 \
  --set-env-vars VITE_API_URL=https://agent-nexus-api-xxx.run.app
```

### Vertex AI Agent Engine (ADK only)

```bash
cd backend
adk deploy --project $PROJECT_ID --location us-central1
```

## Testing

```bash
# Run all tests
cd tests
pytest -v

# Run specific test file
pytest test_agents.py -v

# Run with coverage
pytest --cov=backend --cov-report=html
```

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use type hints for Python code
5. Use TypeScript for frontend code

## License

Apache 2.0
