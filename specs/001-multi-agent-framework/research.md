# Research: Multi-Agent Orchestration Framework

**Date**: 2025-11-04  
**Purpose**: Technical research for implementation decisions

## Overview

This document captures research findings and decisions for key technologies and patterns used in the multi-agent orchestration framework.

## 1. LLM Provider Integration (OpenRouter)

### Decision: OpenRouter API with Extensible Provider Pattern

**Rationale**: OpenRouter provides unified access to multiple LLM models (Claude, GPT-4, etc.) through a single API, reducing integration complexity while allowing model flexibility.

**Key Findings**:
- OpenRouter API is OpenAI-compatible, uses standard chat completion format
- Authentication via `Authorization: Bearer <api-key>` header
- Model selection via `model` parameter in request body
- Rate limiting and quota tracking available via response headers
- Cost tracking per model in API responses

**Implementation Pattern**:
```python
# Abstract provider interface
class LLMProvider(ABC):
    async def spawn_agent(self, model: str, capabilities: List[str]) -> AgentHandle
    async def send_message(self, agent_id: str, message: str) -> Response
    def get_quota_info(self) -> QuotaInfo

# OpenRouter implementation
class OpenRouterProvider(LLMProvider):
    base_url = "https://openrouter.ai/api/v1"
    # ... implementation
```

**Alternatives Considered**:
- Direct API integration per provider - Rejected: Too much duplication, harder to extend
- LangChain/LlamaIndex - Rejected: Heavyweight, more complexity than needed for MVP

---

## 2. Inter-Agent Communication (Message Queue)

### Decision: Redis Pub/Sub with Persistence

**Rationale**: Redis provides lightweight pub/sub messaging with optional persistence, mature Python client (redis-py), and can run embedded or as service.

**Key Findings**:
- Redis pub/sub supports topic-based routing (agents subscribe to topics)
- Pattern matching subscriptions (`agent.*`, `task.completed.*`)
- Persistent streams (Redis Streams) for message replay if needed
- Low latency (<1ms for local Redis)
- Python `redis-py` library has async support (compatible with FastAPI)

**Implementation Pattern**:
```python
# Message queue wrapper
class MessageQueue:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.pubsub = redis_client.pubsub()
    
    async def publish(self, topic: str, message: Message):
        await self.redis.publish(topic, message.json())
    
    async def subscribe(self, pattern: str, handler: Callable):
        await self.pubsub.psubscribe(pattern)
        # async iteration over messages
```

**Message Topics**:
- `agent.{agent_id}.task` - Task assignments to specific agent
- `agent.{agent_id}.status` - Agent status updates
- `workflow.{workflow_id}.events` - Workflow coordination
- `broadcast.*` - System-wide announcements

**Alternatives Considered**:
- RabbitMQ - Rejected: Heavier weight, external service required
- In-memory queues (asyncio.Queue) - Rejected: No persistence, no multi-process support
- File-based message passing - Rejected: Slow, prone to race conditions

---

## 3. Agent Workspace Isolation

### Decision: Filesystem Directories with Python subprocess

**Rationale**: Simple, lightweight isolation sufficient for MVP. Each agent gets dedicated directory with controlled subprocess execution.

**Key Findings**:
- Python `pathlib` provides cross-platform path management
- `subprocess` module with `cwd` parameter enforces workspace directory
- Environment variable isolation via `env` parameter
- Resource limits via `ulimit` (Linux/macOS) or `resource` module

**Implementation Pattern**:
```python
# Workspace creation
workspace_root = Path("workspaces")
agent_workspace = workspace_root / f"agent-{agent.id}"
agent_workspace.mkdir(parents=True, exist_ok=False)

# Workspace structure
agent_workspace/
├── .agent/           # Agent metadata
├── projects/         # Work artifacts
├── .env             # Agent-specific environment
└── logs/            # Execution logs
```

**Security Considerations**:
- Workspaces outside repository root (prevent accidental commits)
- Read-only access to shared templates/scripts
- Filesystem permissions: `chmod 700` (owner only)
- Symlink attacks prevented by absolute path validation

**Alternatives Considered**:
- Docker containers - Deferred: MVP doesn't require full containerization, adds complexity
- Python virtual environments only - Rejected: Insufficient isolation for file operations
- chroot jails - Rejected: Requires root privileges, platform-specific

---

## 4. Real-Time Dashboard Communication

### Decision: FastAPI WebSockets with Event Streaming

**Rationale**: Native FastAPI WebSocket support, efficient for real-time updates, works with standard React WebSocket clients.

**Key Findings**:
- FastAPI WebSocket endpoint: `@app.websocket("/ws/events")`
- Automatic JSON serialization via Pydantic models
- Connection management built-in (handle disconnects gracefully)
- Broadcasting to multiple clients via connection registry

**Implementation Pattern**:
```python
# FastAPI WebSocket endpoint
@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    connections[connection_id] = websocket
    
    try:
        # Subscribe to Redis events
        async for event in event_stream():
            await websocket.send_json(event.dict())
    finally:
        del connections[connection_id]
```

**Event Types Streamed**:
- `agent.spawned`, `agent.paused`, `agent.terminated`
- `task.assigned`, `task.completed`, `task.failed`
- `workflow.started`, `workflow.completed`
- `metrics.updated` (periodic resource metrics)

**Alternatives Considered**:
- Server-Sent Events (SSE) - Rejected: One-way only, WebSockets needed for bidirectional
- Socket.IO - Rejected: Adds library dependency, FastAPI WebSockets sufficient
- HTTP polling - Rejected: Inefficient, higher latency

---

## 5. Task Dependency Resolution

### Decision: Directed Acyclic Graph (DAG) with Topological Sort

**Rationale**: Standard approach for task scheduling, proven algorithms, prevents circular dependencies.

**Key Findings**:
- Python `graphlib.TopologicalSorter` (Python 3.9+) provides built-in DAG sorting
- Cycle detection throws `CycleError` automatically
- Parallel task identification via `get_ready()` method
- State management for partial execution/recovery

**Implementation Pattern**:
```python
from graphlib import TopologicalSorter

# Build task graph
ts = TopologicalSorter()
for task in tasks:
    ts.add(task.id, *task.dependencies)

# Execute in dependency order
ts.prepare()
while ts.is_active():
    ready_tasks = ts.get_ready()
    # Execute ready tasks in parallel
    for task_id in ready_tasks:
        await execute_task(task_id)
        ts.done(task_id)
```

**Alternatives Considered**:
- Custom DFS-based topological sort - Rejected: `graphlib` is standard library, well-tested
- Celery task chains - Rejected: Too heavyweight, external broker required

---

## 6. State Persistence

### Decision: SQLite with SQLAlchemy ORM

**Rationale**: Lightweight, serverless, sufficient for single-machine deployment. SQLAlchemy provides async support and migration tools.

**Key Findings**:
- SQLite `WAL` mode for concurrent reads while writing
- SQLAlchemy async with `asyncio` driver: `sqlite+aiosqlite://`
- Alembic for schema migrations
- JSON columns for flexible metadata storage

**Schema Highlights**:
```sql
-- Agents table
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    capabilities JSON,
    state TEXT CHECK(state IN ('spawning', 'idle', 'working', 'paused', 'error', 'terminated')),
    workspace_path TEXT,
    provider_config JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Events table (append-only log)
CREATE TABLE events (
    id UUID PRIMARY KEY,
    event_type TEXT,
    source_agent_id UUID,
    data JSON,
    severity TEXT,
    timestamp TIMESTAMP
);
CREATE INDEX idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX idx_events_agent ON events(source_agent_id);
```

**Alternatives Considered**:
- PostgreSQL - Rejected: Overkill for MVP, requires external service
- JSON files - Rejected: Poor query performance, no ACID guarantees
- Redis only - Rejected: Not designed for durable state storage

---

## 7. Workflow Visualization (React Flow)

### Decision: React Flow library for node-based editor

**Rationale**: Purpose-built for interactive node graphs, handles drag-and-drop, connections, layout automatically.

**Key Findings**:
- React Flow provides `<ReactFlow>` component with built-in features
- Custom node types via `nodeTypes` prop
- Edge validation callbacks prevent invalid connections
- Layout algorithms available (dagre, elk) for auto-arrangement
- Export/import workflow as JSON

**Implementation Pattern**:
```typescript
import ReactFlow, { Node, Edge } from 'reactflow';

const nodes: Node[] = [
  { id: 'agent-1', type: 'agentNode', position: { x: 100, y: 100 }, data: { capabilities: ['planning'] }},
  { id: 'agent-2', type: 'agentNode', position: { x: 300, y: 100 }, data: { capabilities: ['implementation'] }}
];

const edges: Edge[] = [
  { id: 'e1-2', source: 'agent-1', target: 'agent-2', label: 'plan→code' }
];

function WorkflowEditor() {
  return <ReactFlow nodes={nodes} edges={edges} onConnect={handleConnect} />;
}
```

**Alternatives Considered**:
- D3.js - Rejected: Lower-level, requires more custom implementation
- Cytoscape.js - Rejected: Less React-friendly integration
- Custom Canvas drawing - Rejected: Massive development effort

---

## 8. Performance & Scalability

### Concurrency Model

**Decision**: Python `asyncio` with FastAPI async endpoints

**Rationale**: 
- Native async/await support in Python 3.11+
- FastAPI built on Starlette (async-first)
- Efficient I/O-bound operations (API calls, DB queries, Redis)
- 10-20 concurrent agents feasible with single process

**Key Considerations**:
- Agent operations are I/O-bound (waiting for LLM responses)
- CPU-bound tasks (if any) offloaded to thread pool
- Connection pooling for Redis and SQLite
- WebSocket connection limits managed

**Future Scaling Path** (beyond MVP):
- Horizontal scaling: Multiple backend instances behind load balancer
- Distributed Redis cluster for message queue
- PostgreSQL for multi-instance state sharing
- Container orchestration (Kubernetes) for agent isolation

---

## 9. Error Handling & Resilience

### Retry Strategy

**Decision**: `tenacity` library for declarative retry logic

**Pattern**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def call_provider_api(endpoint, data):
    async with httpx.AsyncClient() as client:
        response = await client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()
```

### Circuit Breaker

**Decision**: Track failure rates, temporarily disable failing providers

**Pattern**: After 5 consecutive failures, mark provider as unhealthy for 60 seconds before retry

### Graceful Degradation

- Agent crash: Other agents continue, failed agent marked for cleanup
- Redis unavailable: Queue in-memory, flush when reconnected
- Dashboard disconnected: Backend continues, reconnect auto-retries

---

## 10. Security Considerations

### API Authentication

**Decision**: API key-based auth for MVP, JWT tokens for future

**Implementation**:
- OpenRouter API keys stored in environment variables
- Dashboard API protected by session tokens
- No agent-to-agent authentication in MVP (trusted environment)

### Workspace Security

**Protections**:
- Path traversal prevention: Validate all paths within workspace
- Symlink resolution: `Path.resolve()` to detect escapes
- File permissions: Agents cannot access other agent workspaces
- No shell injection: Use `subprocess` with argument lists, not strings

### Data Privacy

- Event logs sanitized: Remove sensitive data before logging
- API keys never logged or exposed in responses
- Workspace cleanup on agent termination (optional retention policy)

---

## Summary of Key Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **LLM Provider** | OpenRouter API + Provider pattern | Unified multi-model access, extensible |
| **Messaging** | Redis pub/sub | Lightweight, low-latency, pattern matching |
| **Persistence** | SQLite + SQLAlchemy | Serverless, sufficient for single-machine |
| **Workspace** | Filesystem directories | Simple, cross-platform, MVP-appropriate |
| **API Backend** | FastAPI + asyncio | Async-first, WebSocket support, fast |
| **Dashboard** | React + React Flow | Modern, interactive workflow editor |
| **Task Scheduling** | DAG + topological sort | Proven algorithm, cycle detection |
| **Retry Logic** | tenacity library | Declarative, configurable |
| **Testing** | pytest + httpx mock | Async support, API mocking |

All decisions prioritize:
1. **Simplicity** - Avoid overengineering for MVP
2. **Extensibility** - Provider pattern, plugin architecture
3. **Performance** - Meet success criteria (10s spawn, 5s task assignment, 2s dashboard updates)
4. **Reliability** - Retry logic, error isolation, graceful degradation
5. **Backward Compatibility** - Preserve existing CLI functionality
