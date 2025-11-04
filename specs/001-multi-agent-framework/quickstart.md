# Quickstart: Multi-Agent Orchestration Framework

**Purpose**: Get the multi-agent framework running locally and spawn your first agent

## Prerequisites

- Python 3.11+
- Redis (local or Docker)
- Node.js 18+ (for dashboard)
- Git
- fusion-kit CLI installed

## Setup Steps

### 1. Start Redis

**Option A: Docker** (recommended)
```bash
docker run -d --name fusion-redis -p 6379:6379 redis:7-alpine
```

**Option B: Local Install**
```bash
# macOS
brew install redis
brew services start redis

# Linux (Ubuntu/Debian)
sudo apt install redis-server
sudo systemctl start redis
```

**Verify Redis**:
```bash
redis-cli ping
# Expected output: PONG
```

### 2. Install Dependencies

**Backend**:
```bash
# From repository root
cd /path/to/fusion-kit

# Install Python dependencies
pip install -e ".[multi-agent]"

# Or with specific extras
pip install fastapi[all] redis sqlalchemy[asyncio] aiosqlite pydantic httpx tenacity
```

**Dashboard**:
```bash
cd dashboard
npm install
```

### 3. Initialize Database

```bash
# Create database and run migrations
python -m fusion_kit.persistence.init_db

# Or using Alembic
alembic upgrade head
```

### 4. Configure Environment

Create `.env` file in repository root:

```bash
# LLM Provider
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Redis
REDIS_URL=redis://localhost:6379

# Database
DATABASE_URL=sqlite+aiosqlite:///./fusion_kit.db

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Dashboard
DASHBOARD_URL=http://localhost:3000

# Workspace Root
WORKSPACES_ROOT=./workspaces
```

### 5. Start Backend API

```bash
# Development mode with auto-reload
python -m fusion_kit.api.main --reload

# Or using uvicorn directly
uvicorn fusion_kit.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify backend**:
```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy"}
```

### 6. Start Dashboard (Optional)

```bash
cd dashboard
npm run dev
```

Visit: `http://localhost:3000`

## Your First Agent

### Option 1: CLI

```bash
# Create a project
fusion-kit project create "my-project"

# Spawn an agent
fusion-kit agent spawn \
  --name "CodeReviewer" \
  --capabilities "code_review,python" \
  --model "anthropic/claude-3-opus" \
  --project "my-project"

# Check agent status
fusion-kit agent list

# View agent details
fusion-kit agent get <agent-id>
```

### Option 2: Python API

```python
import asyncio
from fusion_kit.core.agent import AgentManager
from fusion_kit.providers.openrouter import OpenRouterProvider

async def spawn_first_agent():
    # Initialize provider
    provider = OpenRouterProvider(api_key="your_openrouter_api_key_here")
    
    # Create agent manager
    manager = AgentManager(provider)
    
    # Spawn agent
    agent = await manager.spawn_agent(
        name="CodeReviewer",
        capabilities=["code_review", "python"],
        model="anthropic/claude-3-opus",
        project_id="my-project-id"
    )
    
    print(f"Agent spawned: {agent.id}")
    print(f"Workspace: {agent.workspace_path}")
    print(f"State: {agent.state}")
    
    return agent

# Run
agent = asyncio.run(spawn_first_agent())
```

### Option 3: REST API

```bash
# Spawn agent
curl -X POST http://localhost:8000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CodeReviewer",
    "capabilities": ["code_review", "python"],
    "provider_id": "<provider-uuid>",
    "model_name": "anthropic/claude-3-opus",
    "project_id": "<project-uuid>"
  }'

# List agents
curl http://localhost:8000/api/v1/agents

# Get agent details
curl http://localhost:8000/api/v1/agents/<agent-id>
```

## Assign Your First Task

```bash
# Create task
fusion-kit task create \
  --name "Review pull request" \
  --description "Review PR #123 for code quality and best practices" \
  --capabilities "code_review" \
  --priority 1

# Task will auto-assign to agent with matching capabilities

# Check task status
fusion-kit task list

# View task output
fusion-kit task get <task-id>
```

## Create a Simple Workflow

```python
from fusion_kit.coordination.workflow_engine import WorkflowEngine

async def create_code_review_workflow():
    engine = WorkflowEngine()
    
    # Define workflow DAG
    workflow = await engine.create_workflow(
        name="Code Review Pipeline",
        dag_definition={
            "nodes": [
                {"id": "analyze", "agent_capabilities": ["static_analysis"]},
                {"id": "review", "agent_capabilities": ["code_review"]},
                {"id": "report", "agent_capabilities": ["documentation"]}
            ],
            "edges": [
                {"source": "analyze", "target": "review"},
                {"source": "review", "target": "report"}
            ]
        }
    )
    
    # Start workflow
    await engine.start_workflow(workflow.id)
    
    return workflow
```

## Monitor in Dashboard

1. **Open dashboard**: http://localhost:3000
2. **View agents**: Click "Agents" tab - see all active agents
3. **Monitor tasks**: Click "Tasks" tab - see task queue and assignments
4. **View events**: Click "Monitoring" tab - real-time event stream
5. **Create workflow**: Click "Workflows" tab - drag-and-drop editor

## Test Inter-Agent Communication

```python
from fusion_kit.messaging.message_queue import MessageQueue

async def send_message_between_agents():
    mq = MessageQueue(redis_url="redis://localhost:6379")
    
    # Agent 1 publishes message
    await mq.publish(
        topic="agent.agent-2-id.task",
        message={
            "type": "collaboration_request",
            "from": "agent-1-id",
            "payload": {"request": "Need help with code review"}
        }
    )
    
    # Agent 2 subscribes and receives
    async def handle_message(message):
        print(f"Received: {message}")
    
    await mq.subscribe("agent.agent-2-id.*", handle_message)
```

## Verify Success

Run this verification script:

```bash
python -m fusion_kit.cli.verify
```

**Expected checks**:
- ✅ Redis connection established
- ✅ Database initialized
- ✅ At least one provider configured
- ✅ Workspaces directory created
- ✅ API server responding
- ✅ Message queue functional

## Common Issues

### Redis Connection Failed

```bash
# Check Redis status
redis-cli ping

# Restart Redis (Docker)
docker restart fusion-redis

# Restart Redis (systemctl)
sudo systemctl restart redis
```

### Database Locked

```bash
# SQLite WAL mode not enabled
# Add to DATABASE_URL: ?timeout=20&check_same_thread=False
```

### Agent Spawn Timeout

```bash
# Check provider API key
echo $OPENROUTER_API_KEY

# Test provider connectivity
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"
```

### Workspace Permission Denied

```bash
# Fix workspace permissions
chmod 755 workspaces
chmod 700 workspaces/agent-*
```

## Next Steps

1. **Explore Examples**: `examples/multi-agent/`
2. **Read Docs**: `specs/001-multi-agent-framework/`
3. **Run Tests**: `pytest tests/integration/test_agent_spawning.py`
4. **Join Community**: GitHub Discussions

## CLI Reference

```bash
# Project commands
fusion-kit project create <name>
fusion-kit project list
fusion-kit project delete <id>

# Agent commands
fusion-kit agent spawn --help
fusion-kit agent list [--state idle]
fusion-kit agent get <id>
fusion-kit agent pause <id>
fusion-kit agent resume <id>
fusion-kit agent terminate <id>
fusion-kit agent logs <id>

# Task commands
fusion-kit task create --help
fusion-kit task list [--state queued]
fusion-kit task get <id>
fusion-kit task cancel <id>

# Workflow commands
fusion-kit workflow create <definition.yaml>
fusion-kit workflow list
fusion-kit workflow start <id>
fusion-kit workflow validate <id>

# Monitoring commands
fusion-kit events tail [--follow]
fusion-kit metrics agent <id>
fusion-kit health

# Dashboard command
fusion-kit dashboard start [--port 3000]
```

## Development Mode

```bash
# Backend with debug logging
FUSION_DEBUG=1 python -m fusion_kit.api.main

# Dashboard with hot reload
cd dashboard && npm run dev

# Run tests
pytest -v

# Watch mode for tests
pytest-watch
```

## Production Deployment (Future)

See `docs/deployment.md` for:
- Docker Compose setup
- Kubernetes manifests
- Load balancer configuration
- Multi-instance Redis cluster
- PostgreSQL migration from SQLite
