# Backend Architect - Implementation Instructions

## Mission
Build the foundational backend infrastructure for the multi-agent orchestration framework. Your work is **CRITICAL** and **BLOCKS** all other agents until Phase 2 is complete.

## Context
- **Project**: fusion-kit multi-agent framework
- **Branch**: `001-multi-agent-framework`
- **Spec**: `specs/001-multi-agent-framework/`
- **Role**: Backend Infrastructure & Core Systems

## Phase 1: Setup (T001-T010) - PARALLEL with others

### Task: Create Package Structure

Execute these in sequence:

```bash
cd /home/hyperuser/fusion-kit

# Create main package
mkdir -p src/fusion_kit
touch src/fusion_kit/__init__.py

# Create submodules
mkdir -p src/fusion_kit/{core,providers,coordination,messaging,monitoring,persistence,api,cli}
touch src/fusion_kit/core/__init__.py
touch src/fusion_kit/providers/__init__.py
touch src/fusion_kit/coordination/__init__.py
touch src/fusion_kit/messaging/__init__.py
touch src/fusion_kit/monitoring/__init__.py
touch src/fusion_kit/persistence/__init__.py
touch src/fusion_kit/api/__init__.py
touch src/fusion_kit/cli/__init__.py
```

### Task: Update Dependencies

Add to `pyproject.toml`:

```toml
[project.dependencies]
# Existing dependencies remain
# Add these for multi-agent framework:
"fastapi[all]>=0.109.0",
"redis>=5.0.0",
"sqlalchemy[asyncio]>=2.0.0",
"aiosqlite>=0.19.0",
"pydantic>=2.5.0",
"httpx>=0.26.0",
"tenacity>=8.2.0",
```

**Checkpoint**: Package structure created ✓

---

## Phase 2: Foundation (T015-T030) - **CRITICAL - BLOCKS ALL**

### 🚨 ATTENTION: This phase MUST complete before other agents can proceed

### Part A: Database & Persistence (T015-T019)

**File**: `src/fusion_kit/persistence/models.py`

Implement ALL 10 SQLAlchemy models from `specs/001-multi-agent-framework/data-model.md`:
1. Agent
2. Task
3. Workspace
4. Workflow
5. Event
6. Message
7. Capability
8. Project
9. ResourceMetrics
10. ProviderConfig

**File**: `src/fusion_kit/persistence/init_db.py`
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "sqlite+aiosqlite:///./fusion_kit.db"

async def init_db():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

**File**: `src/fusion_kit/persistence/repositories.py`

Create async CRUD operations for all models.

**Validation**: Run `python -m fusion_kit.persistence.init_db` - database should be created.

### Part B: Message Queue (T020-T023)

**File**: `src/fusion_kit/messaging/message_queue.py`

```python
import redis.asyncio as redis
import json

class MessageQueue:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
    
    async def publish(self, topic: str, message: dict):
        await self.redis.publish(topic, json.dumps(message))
    
    async def subscribe(self, pattern: str):
        await self.pubsub.psubscribe(pattern)
        async for message in self.pubsub.listen():
            if message['type'] == 'pmessage':
                yield json.loads(message['data'])
```

**Validation**: Connect to Redis, publish/subscribe test message.

### Part C: Provider System (T024-T026)

**File**: `src/fusion_kit/providers/base.py`

```python
from abc import ABC, abstractmethod
from typing import List, Dict
from uuid import UUID

class LLMProvider(ABC):
    @abstractmethod
    async def spawn_agent(self, model: str, capabilities: List[str]) -> Dict:
        pass
    
    @abstractmethod
    async def send_message(self, agent_id: UUID, message: str) -> Dict:
        pass
    
    @abstractmethod
    def get_quota_info(self) -> Dict:
        pass
```

**File**: `src/fusion_kit/providers/registry.py`

Provider plugin system with registration.

**Validation**: Can register a provider, retrieve it by name.

### Part D: FastAPI Foundation (T027-T030)

**File**: `src/fusion_kit/api/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Fusion Kit Multi-Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}
```

**Validation**: Run `uvicorn fusion_kit.api.main:app` - server starts, health endpoint responds.

**🚨 CHECKPOINT**: Foundation complete. Signal to other agents they can proceed.

---

## Phase 3: US1 Core (T031-T040)

### Agent Core Classes (T031-T035)

**File**: `src/fusion_kit/core/agent.py`

```python
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime

class AgentState(str, Enum):
    SPAWNING = "spawning"
    IDLE = "idle"
    WORKING = "working"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"

class Agent:
    def __init__(self, name: str, capabilities: List[str], provider_id: UUID):
        self.id = uuid4()
        self.name = name
        self.state = AgentState.SPAWNING
        self.capabilities = capabilities
        self.provider_id = provider_id
        self.created_at = datetime.utcnow()
    
    def transition_to(self, new_state: AgentState):
        # Implement state machine logic
        valid_transitions = {
            AgentState.SPAWNING: [AgentState.IDLE, AgentState.ERROR],
            AgentState.IDLE: [AgentState.WORKING, AgentState.PAUSED, AgentState.TERMINATED],
            # ... etc
        }
        if new_state not in valid_transitions.get(self.state, []):
            raise ValueError(f"Invalid transition: {self.state} -> {new_state}")
        self.state = new_state
```

**File**: `src/fusion_kit/core/workspace.py` - Implement workspace isolation with filesystem operations.

**File**: `src/fusion_kit/core/lifecycle.py` - AgentManager with spawn/pause/resume/terminate.

### OpenRouter Provider (T036-T040)

**File**: `src/fusion_kit/providers/openrouter.py`

Implement OpenRouter API client per `specs/001-multi-agent-framework/research.md` section 1.

**Validation**: Spawn a test agent, verify workspace created, state transitions work.

---

## Communication Protocol

After completing each checkpoint:

1. Update `.droid/status/backend-architect.json`:
```json
{
  "agent": "backend-architect",
  "phase": "phase_2_complete",
  "timestamp": "2025-11-04T...",
  "tasks_completed": ["T015", "T016", ...],
  "checkpoint_validated": true,
  "blocking_released": true
}
```

2. Commit your work:
```bash
git add src/fusion_kit/
git commit -m "feat(backend): implement foundation (T015-T030)

- Add SQLAlchemy models for 10 entities
- Implement Redis message queue
- Create provider interface and registry
- Setup FastAPI application with health check
- Add database initialization and migrations

Foundation checkpoint complete. Other agents can proceed.
"
```

---

## Success Criteria

- [ ] All 10 database models implemented and tested
- [ ] Redis pub/sub working
- [ ] Provider interface defined and registry functional
- [ ] FastAPI app starts and health check responds
- [ ] Agent class state machine works
- [ ] Workspace isolation verified (create 2 agents, check separate directories)
- [ ] OpenRouter provider can make API call

**CRITICAL**: Do not signal completion until ALL checkpoints pass.

---

## Reference Documents

1. `specs/001-multi-agent-framework/data-model.md` - Entity definitions
2. `specs/001-multi-agent-framework/research.md` - Technology decisions
3. `specs/001-multi-agent-framework/plan.md` - Architecture
4. `specs/001-multi-agent-framework/tasks.md` - Full task list

**Priority**: P1 - CRITICAL PATH. Your completion gates all other agents.
