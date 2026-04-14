# Vertex Cowork Best Practices

## Agent Design

### 1. Single Responsibility

Each agent should have a focused, well-defined purpose.

**Good:**
```python
# Separate agents for different tasks
research_agent = AgentConfig(
    agent_id="research",
    name="Research Agent",
    system_prompt="You research topics and provide summaries.",
)

writing_agent = AgentConfig(
    agent_id="writing",
    name="Writing Agent", 
    system_prompt="You write content based on research.",
)
```

**Avoid:**
```python
# One agent trying to do everything
do_everything_agent = AgentConfig(
    agent_id="everything",
    system_prompt="You research, write, code, debug, deploy...",
)
```

### 2. Tool Selection

Only include tools the agent actually needs.

**Good:**
```python
# Research agent only needs search tools
research_agent = AgentConfig(
    agent_id="research",
    tools=["web_search", "document_search"],
)
```

**Avoid:**
```python
# Don't give all tools to every agent
research_agent = AgentConfig(
    tools=["search", "write_file", "execute_code", "send_email", "deploy", ...],
)
```

### 3. System Prompts

Be specific about the agent's role and constraints.

**Good:**
```python
system_prompt = """You are a code review assistant.

Your responsibilities:
1. Review code for bugs and security issues
2. Suggest improvements for readability
3. Check for best practices violations

Constraints:
- Only review code, don't write new features
- Be constructive in feedback
- Cite specific line numbers
- Maximum 5 suggestions per review
"""
```

**Avoid:**
```python
system_prompt = "You are helpful."
```

### 4. Temperature Settings

| Task Type | Temperature | Rationale |
|-----------|-------------|-----------|
| Code generation | 0.1 - 0.3 | Deterministic, correct |
| Factual Q&A | 0.1 - 0.3 | Accurate, consistent |
| Creative writing | 0.7 - 1.0 | Diverse, creative |
| Brainstorming | 0.8 - 1.2 | Exploratory |

## Multi-Agent Systems

### 1. Supervisor Pattern

Best for dynamic routing based on input.

```python
supervisor = AgentConfig(
    agent_id="supervisor",
    agent_type="supervisor",
    system_prompt="""Route requests to the appropriate specialist:
    - research_agent: For finding information
    - code_agent: For writing or reviewing code
    - writing_agent: For content creation
    """,
    subagents=["research_agent", "code_agent", "writing_agent"],
)
```

**When to use:**
- Complex queries requiring expertise selection
- Dynamic workflows
- User-facing orchestration

### 2. Sequential Pattern

Best for pipeline processing.

```python
pipeline = AgentConfig(
    agent_id="content-pipeline",
    agent_type="sequential",
    subagents=["research", "outline", "write", "edit", "format"],
)
```

**When to use:**
- Step-by-step workflows
- Each step depends on previous output
- Clear transformation pipeline

### 3. Parallel Pattern

Best for independent subtasks.

```python
parallel_search = AgentConfig(
    agent_id="multi-search",
    agent_type="parallel",
    subagents=["web_search", "db_search", "doc_search"],
)
```

**When to use:**
- Independent data gathering
- Redundant processing for reliability
- Speed optimization

## MCP Server Security

### 1. Principle of Least Privilege

```python
# Only expose necessary directories
{
    "command": "npx server-filesystem /app/data/user-uploads",
    # NOT: "npx server-filesystem /"
}
```

### 2. Input Validation

Validate all tool arguments before execution:

```python
@server.tool()
async def safe_file_read(path: str) -> str:
    # Validate path is within allowed directory
    allowed_dir = Path("/app/data")
    requested = (allowed_dir / path).resolve()
    
    if not str(requested).startswith(str(allowed_dir)):
        raise ValueError("Access denied: path outside allowed directory")
    
    return requested.read_text()
```

### 3. Audit Logging

Log all tool calls for security review:

```python
logger.info(
    "mcp_tool_called",
    server_id=server_id,
    tool_name=tool_name,
    arguments=sanitized_args,  # Redact sensitive data
    user_id=user_id,
    timestamp=datetime.utcnow(),
)
```

## Evaluation Best Practices

### 1. Golden Datasets

Create comprehensive test cases covering:

- Happy path scenarios
- Edge cases
- Error handling
- Tool usage patterns

```python
evaluation_cases = [
    EvaluationCase(
        case_id="basic-greeting",
        input_message="Hello",
        expected_content_contains=["hello", "help"],
    ),
    EvaluationCase(
        case_id="search-request",
        input_message="Search for Python tutorials",
        expected_tools=["web_search"],
        expected_content_contains=["python", "tutorial"],
    ),
    EvaluationCase(
        case_id="error-handling",
        input_message="Do something impossible",
        expected_content_not_contains=["error", "failed"],
    ),
]
```

### 2. Tool Trajectory Testing

Verify expected tool sequences:

```python
# Exact order: tools must appear in exact sequence
EvaluationCase(
    expected_tools=["search", "summarize", "format"],
    expected_tool_order="exact",
)

# In order: tools appear in order, but may have others between
EvaluationCase(
    expected_tools=["search", "format"],
    expected_tool_order="in_order",
)

# Any: all tools called, any order
EvaluationCase(
    expected_tools=["search", "validate"],
    expected_tool_order="any",
)
```

### 3. Continuous Evaluation

Run evaluations automatically:

```bash
# In CI/CD pipeline
pytest tests/test_evaluation.py -v --tb=short

# On schedule
0 * * * * cd /app && python -m evaluation.run_all
```

## Performance Optimization

### 1. Model Selection

| Use Case | Recommended Model |
|----------|-------------------|
| Simple chat | gemini-2.0-flash |
| Complex reasoning | gemini-2.0-pro |
| Long context | gemini-2.5-pro-preview |
| Code generation | claude-3-5-sonnet |

### 2. Caching

Cache expensive operations:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text: str) -> list[float]:
    return model.embed(text)
```

### 3. Streaming

Use streaming for better UX:

```python
# Enable streaming for long responses
response = await client.post(
    f"/api/agents/{agent_id}/chat",
    json={"message": message, "stream": True},
)
```

## Error Handling

### 1. Graceful Degradation

```python
try:
    result = await mcp_client.call_tool("search", {"query": query})
except MCPConnectionError:
    # Fallback to cached results or alternative
    result = await get_cached_results(query)
except MCPToolError as e:
    # Log and return helpful error message
    logger.error("mcp_tool_error", error=str(e))
    return "I couldn't complete the search. Please try again."
```

### 2. Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
async def call_with_retry(tool_name: str, args: dict) -> Any:
    return await mcp_client.call_tool(tool_name, args)
```

### 3. Circuit Breaker

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
async def call_external_service(request: dict) -> dict:
    return await service.call(request)
```
