# Integration Engineer - Implementation Instructions

## Mission
Build REST API endpoints and CLI commands for agent management and task coordination.

## Context
- **Project**: fusion-kit multi-agent framework
- **Branch**: `001-multi-agent-framework`
- **Working Directory**: `/home/hyperuser/fusion-kit`
- **Specification**: `specs/001-multi-agent-framework/`
- **Role**: API Endpoints & CLI Commands

## Dependencies
⏳ **WAITING**: Backend architect must complete Phase 2 (Foundation) before you proceed
- You CAN start planning/review after backend Phase 2
- You CANNOT implement until core models/services available

## Phase 3: US1 - Agent API Endpoints & CLI (T041-T055)

**Status**: BLOCKED until backend Phase 2 complete

### Agent API Endpoints (T041-T046)

**File**: `src/fusion_kit/api/agents.py`

```python
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from ..core.lifecycle import AgentManager
from ..persistence.repositories import AgentRepository

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

class AgentResponse(BaseModel):
    id: UUID
    name: str
    state: str
    capabilities: List[str]
    workspace_path: str
    created_at: str

class AgentCreate(BaseModel):
    name: str
    capabilities: List[str]
    provider_id: UUID
    model_name: str
    project_id: UUID

@router.get("", response_model=dict)
async def list_agents(
    state: Optional[str] = Query(None),
    project_id: Optional[UUID] = Query(None),
    repo: AgentRepository = Depends()
):
    """List all agents with optional filtering"""
    agents = await repo.list_agents(state=state, project_id=project_id)
    return {"agents": agents, "total": len(agents)}

@router.post("", response_model=AgentResponse, status_code=201)
async def spawn_agent(
    data: AgentCreate,
    manager: AgentManager = Depends()
):
    """Spawn new agent"""
    try:
        agent = await manager.spawn_agent(
            name=data.name,
            capabilities=data.capabilities,
            provider_id=data.provider_id,
            model_name=data.model_name,
            project_id=data.project_id
        )
        return agent
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    repo: AgentRepository = Depends()
):
    """Get agent details"""
    agent = await repo.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    action: str = Query(...),
    manager: AgentManager = Depends()
):
    """Pause, resume, or update agent"""
    if action == "pause":
        agent = await manager.pause_agent(agent_id)
    elif action == "resume":
        agent = await manager.resume_agent(agent_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    return agent

@router.delete("/{agent_id}", status_code=204)
async def terminate_agent(
    agent_id: UUID,
    manager: AgentManager = Depends()
):
    """Terminate agent"""
    await manager.terminate_agent(agent_id)

@router.get("/{agent_id}/metrics")
async def get_agent_metrics(
    agent_id: UUID,
    since: Optional[str] = Query(None),
    limit: int = Query(100),
    repo = Depends()
):
    """Get agent resource metrics"""
    metrics = await repo.get_metrics(agent_id, since=since, limit=limit)
    return {"metrics": metrics}
```

### CLI Commands (T047-T052)

**File**: `src/fusion_kit/cli/agent_cmd.py`

```python
import typer
from typing import Optional, List
from uuid import UUID
from rich.console import Console
from ..core.lifecycle import AgentManager
from ..persistence.repositories import AgentRepository

console = Console()
app = typer.Typer(help="Agent management commands")

@app.command()
def spawn(
    name: str = typer.Option(..., help="Agent name"),
    capabilities: str = typer.Option(..., help="Comma-separated capabilities"),
    model: str = typer.Option(..., help="LLM model name"),
    project_id: str = typer.Option(..., help="Project UUID"),
    provider_id: str = typer.Option(..., help="Provider UUID"),
):
    """Spawn new agent"""
    console.print(f"[cyan]Spawning agent '{name}'...")
    # Implementation
    console.print(f"[green]✓ Agent spawned: {agent_id}")

@app.command()
def list(
    state: Optional[str] = typer.Option(None, help="Filter by state"),
    project_id: Optional[str] = typer.Option(None, help="Filter by project"),
):
    """List agents"""
    # Implementation
    # Display agents in table format

@app.command()
def get(agent_id: str = typer.Argument(..., help="Agent UUID")):
    """Get agent details"""
    # Implementation
    # Display agent details

@app.command()
def pause(agent_id: str = typer.Argument(..., help="Agent UUID")):
    """Pause agent"""
    console.print(f"[yellow]Pausing agent {agent_id}...")
    # Implementation
    console.print("[green]✓ Agent paused")

@app.command()
def resume(agent_id: str = typer.Argument(..., help="Agent UUID")):
    """Resume agent"""
    console.print(f"[cyan]Resuming agent {agent_id}...")
    # Implementation
    console.print("[green]✓ Agent resumed")

@app.command()
def terminate(agent_id: str = typer.Argument(..., help="Agent UUID")):
    """Terminate agent"""
    console.print(f"[red]Terminating agent {agent_id}...")
    # Implementation
    console.print("[green]✓ Agent terminated")
```

### Event Logging (T053-T055)

**File**: `src/fusion_kit/monitoring/event_logger.py`

```python
from datetime import datetime
from typing import Any, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from ..persistence.models import Event

class EventLogger:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def log_event(
        self,
        event_type: str,
        severity: str = "info",
        source_agent_id: Optional[UUID] = None,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
    ):
        """Log an event to database"""
        event = Event(
            event_type=event_type,
            severity=severity,
            source_agent_id=source_agent_id,
            data=data or {},
            message=message,
            timestamp=datetime.utcnow(),
        )
        self.session.add(event)
        await self.session.commit()
    
    async def log_agent_spawned(self, agent_id: UUID, name: str):
        await self.log_event(
            "agent.spawned",
            severity="info",
            source_agent_id=agent_id,
            message=f"Agent '{name}' spawned"
        )
    
    async def log_agent_paused(self, agent_id: UUID):
        await self.log_event(
            "agent.paused",
            severity="info",
            source_agent_id=agent_id,
            message=f"Agent paused"
        )
    
    async def log_agent_error(self, agent_id: UUID, error: str):
        await self.log_event(
            "agent.error",
            severity="error",
            source_agent_id=agent_id,
            message=f"Agent error: {error}"
        )
```

**Validation**:
- All endpoints respond correctly
- CLI commands work and format output nicely
- Events logged to database

**Checkpoint**: US1 APIs & CLI complete ✓

---

## Phase 5: US3 - Task & Workflow APIs (T087-T110)

**Status**: BLOCKED until Phase 3 complete

### Task API Endpoints (T087-T090)

**File**: `src/fusion_kit/api/tasks.py`

```python
from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from ..coordination.task_queue import TaskQueue
from ..persistence.repositories import TaskRepository

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

class TaskCreate(BaseModel):
    name: str
    description: str
    required_capabilities: List[str]
    priority: int = 0
    dependencies: List[UUID] = []
    workflow_id: Optional[UUID] = None
    input_artifacts: dict = {}

@router.get("")
async def list_tasks(
    state: Optional[str] = Query(None),
    agent_id: Optional[UUID] = Query(None),
    workflow_id: Optional[UUID] = Query(None),
    repo: TaskRepository = Depends()
):
    """List tasks with filtering"""
    tasks = await repo.list_tasks(state=state, agent_id=agent_id, workflow_id=workflow_id)
    return {"tasks": tasks}

@router.post("", status_code=201)
async def create_task(
    data: TaskCreate,
    queue: TaskQueue = Depends()
):
    """Create task"""
    task = await queue.add_task(
        name=data.name,
        description=data.description,
        required_capabilities=data.required_capabilities,
        priority=data.priority,
        dependencies=data.dependencies,
        workflow_id=data.workflow_id,
        input_artifacts=data.input_artifacts
    )
    return task

@router.get("/{task_id}")
async def get_task(task_id: UUID, repo: TaskRepository = Depends()):
    """Get task details"""
    task = await repo.get_task(task_id)
    return task

@router.patch("/{task_id}")
async def update_task(task_id: UUID, state: Optional[str] = None):
    """Update task state"""
    # Implementation
    pass
```

### Workflow API Endpoints (T106-T110)

**File**: `src/fusion_kit/api/workflows.py`

```python
from fastapi import APIRouter, Depends
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from ..coordination.workflow_engine import WorkflowEngine
from ..persistence.repositories import WorkflowRepository

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    dag_definition: dict
    execution_parameters: dict = {}
    project_id: UUID

@router.get("")
async def list_workflows(
    state: Optional[str] = None,
    project_id: Optional[UUID] = None,
    repo: WorkflowRepository = Depends()
):
    """List workflows"""
    workflows = await repo.list_workflows(state=state, project_id=project_id)
    return {"workflows": workflows}

@router.post("", status_code=201)
async def create_workflow(data: WorkflowCreate):
    """Create workflow"""
    # Implementation
    pass

@router.get("/{workflow_id}")
async def get_workflow(workflow_id: UUID, repo: WorkflowRepository = Depends()):
    """Get workflow details"""
    workflow = await repo.get_workflow(workflow_id)
    return workflow

@router.post("/{workflow_id}/start")
async def start_workflow(
    workflow_id: UUID,
    engine: WorkflowEngine = Depends()
):
    """Start workflow execution"""
    workflow = await engine.start_workflow(workflow_id)
    return workflow

@router.post("/{workflow_id}/validate")
async def validate_workflow(
    workflow_id: UUID,
    engine: WorkflowEngine = Depends()
):
    """Validate workflow DAG"""
    result = await engine.validate_workflow(workflow_id)
    return result
```

**Validation**:
- All task endpoints working
- All workflow endpoints working
- Validation detects cycles
- Workflows execute in order

**Checkpoint**: US3 APIs complete ✓

---

## Success Criteria

- [ ] All agent endpoints respond correctly (list, spawn, get, pause, resume, terminate)
- [ ] CLI commands work with proper output formatting
- [ ] All task endpoints functional
- [ ] All workflow endpoints functional
- [ ] Error handling with proper HTTP status codes
- [ ] Events logged for all agent operations

## Communication Protocol

After Phase 3:
```json
{
  "agent": "integration-engineer",
  "phase": "phase_3_us1_complete",
  "tasks_completed": ["T041", ..., "T055"],
  "checkpoint_validated": true
}
```

After Phase 5:
```json
{
  "agent": "integration-engineer",
  "phase": "phase_5_us3_complete",
  "tasks_completed": ["T087", ..., "T110"],
  "checkpoint_validated": true
}
```

**Priority**: P2 - Start after backend Phase 2 complete
