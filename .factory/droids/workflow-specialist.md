# Workflow Specialist - Implementation Instructions

## Mission
Implement task coordination, dependency resolution, and multi-agent workflow orchestration.

## Context
- **Project**: fusion-kit multi-agent framework
- **Branch**: `001-multi-agent-framework`
- **Working Directory**: `/home/hyperuser/fusion-kit`
- **Role**: Task Coordination & Workflows

## Dependencies
⏳ **MUST WAIT**: 
- Backend Phase 2 (database, Redis, provider system)
- Integration engineer Phase 3 (API endpoints for tasks/workflows)

## Phase 5: US3 - Task Coordination & Workflows (T084-T105)

### Task Management (T084-T086)

**File**: `src/fusion_kit/coordination/task_queue.py`

```python
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class TaskState(str, Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    id: UUID
    name: str
    state: TaskState
    priority: int
    required_capabilities: List[str]
    agent_id: Optional[UUID] = None
    dependencies: List[UUID] = None
    queued_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None

class TaskQueue:
    def __init__(self, db_session):
        self.db_session = db_session
        self.queue: List[Task] = []
    
    async def add_task(
        self,
        name: str,
        required_capabilities: List[str],
        priority: int = 0,
        dependencies: List[UUID] = None
    ) -> Task:
        """Add task to queue"""
        task = Task(
            id=uuid4(),
            name=name,
            state=TaskState.QUEUED,
            priority=priority,
            required_capabilities=required_capabilities,
            dependencies=dependencies or [],
            queued_at=datetime.utcnow()
        )
        self.queue.append(task)
        # Persist to database
        await self.db_session.add(task)
        return task
    
    async def get_ready_tasks(self) -> List[Task]:
        """Get tasks with all dependencies satisfied"""
        ready = []
        for task in self.queue:
            if task.state == TaskState.QUEUED:
                # Check if all dependencies completed
                all_deps_done = all(
                    self._is_task_completed(dep_id)
                    for dep_id in task.dependencies
                )
                if all_deps_done:
                    ready.append(task)
        return ready
    
    def _is_task_completed(self, task_id: UUID) -> bool:
        """Check if task is completed"""
        # Implementation
        pass
```

### Delegation Daemon (T091-T094)

**File**: `src/fusion_kit/coordination/delegation_daemon.py`

```python
import asyncio
from typing import Dict, List, Optional
from uuid import UUID
from .task_queue import TaskQueue
from ..persistence.repositories import AgentRepository

class DelegationDaemon:
    def __init__(self, task_queue: TaskQueue, agent_repo: AgentRepository):
        self.task_queue = task_queue
        self.agent_repo = agent_repo
        self.running = False
    
    async def start(self):
        """Start delegation daemon"""
        self.running = True
        while self.running:
            # Get ready tasks
            ready_tasks = await self.task_queue.get_ready_tasks()
            
            # Assign to agents
            for task in ready_tasks:
                agent = await self._find_best_agent(task)
                if agent:
                    await self._assign_task(task, agent)
            
            await asyncio.sleep(5)  # Check every 5 seconds
    
    async def stop(self):
        """Stop delegation daemon"""
        self.running = False
    
    async def _find_best_agent(self, task) -> Optional[Agent]:
        """Find best agent for task based on capabilities and workload"""
        # Get available agents
        idle_agents = await self.agent_repo.get_agents_by_state("idle")
        
        # Filter by capabilities
        capable_agents = [
            a for a in idle_agents
            if all(cap in a.capabilities for cap in task.required_capabilities)
        ]
        
        # Sort by workload (fewer tasks = higher priority)
        capable_agents.sort(key=lambda a: a.current_task_count)
        
        return capable_agents[0] if capable_agents else None
    
    async def _assign_task(self, task, agent):
        """Assign task to agent"""
        # Update task state
        task.agent_id = agent.id
        task.state = TaskState.ASSIGNED
        
        # Send message to agent
        await self._send_task_to_agent(agent, task)
    
    async def _send_task_to_agent(self, agent, task):
        """Send task to agent via message queue"""
        # Implementation using message queue
        pass
```

### Dependency Resolver (T095-T097)

**File**: `src/fusion_kit/coordination/dependency_resolver.py`

```python
from typing import List, Dict, Set
from uuid import UUID
from graphlib import TopologicalSorter

class DependencyResolver:
    def __init__(self):
        self.tasks: Dict[UUID, Dict] = {}
    
    def add_task(self, task_id: UUID, dependencies: List[UUID]):
        """Add task with dependencies"""
        self.tasks[task_id] = {"dependencies": dependencies}
    
    def resolve_order(self) -> List[UUID]:
        """Return tasks in dependency order"""
        ts = TopologicalSorter()
        
        for task_id, task_info in self.tasks.items():
            ts.add(task_id, *task_info["dependencies"])
        
        try:
            return list(ts.static_order())
        except Exception as e:
            raise ValueError(f"Circular dependency detected: {e}")
    
    def get_ready_tasks(self, completed: Set[UUID]) -> List[UUID]:
        """Get tasks ready to execute"""
        ready = []
        for task_id, task_info in self.tasks.items():
            if task_id not in completed:
                # Check if all dependencies completed
                if all(dep in completed for dep in task_info["dependencies"]):
                    ready.append(task_id)
        return ready
```

### Inter-Agent Messaging (T098-T101)

**File**: `src/fusion_kit/coordination/message_router.py`

```python
from typing import Dict, Any, List, Callable
from uuid import UUID
from ..messaging.message_queue import MessageQueue

class MessageRouter:
    def __init__(self, message_queue: MessageQueue):
        self.mq = message_queue
        self.handlers: Dict[str, List[Callable]] = {}
    
    async def route_message(self, message: Dict[str, Any]):
        """Route message to appropriate handlers"""
        message_type = message.get("type")
        
        if message_type in self.handlers:
            for handler in self.handlers[message_type]:
                await handler(message)
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler"""
        if message_type not in self.handlers:
            self.handlers[message_type] = []
        self.handlers[message_type].append(handler)
    
    async def send_task_result(
        self,
        from_agent: UUID,
        to_agent: UUID,
        task_id: UUID,
        result: Dict[str, Any]
    ):
        """Send task result from one agent to another"""
        message = {
            "type": "task_result",
            "from_agent": str(from_agent),
            "task_id": str(task_id),
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to agent's topic
        await self.mq.publish(f"agent.{to_agent}.tasks", message)
```

### Workflow Engine (T102-T105)

**File**: `src/fusion_kit/coordination/workflow_engine.py`

```python
from typing import List, Dict, Optional
from uuid import UUID
from dataclasses import dataclass
from enum import Enum
from .dependency_resolver import DependencyResolver
from .task_queue import TaskQueue

class WorkflowState(str, Enum):
    DRAFT = "draft"
    VALIDATING = "validating"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Workflow:
    id: UUID
    name: str
    state: WorkflowState
    dag_definition: Dict
    tasks: List[UUID] = None

class WorkflowEngine:
    def __init__(self, task_queue: TaskQueue):
        self.task_queue = task_queue
        self.workflows: Dict[UUID, Workflow] = {}
    
    async def create_workflow(
        self,
        name: str,
        dag_definition: Dict,
        project_id: UUID
    ) -> Workflow:
        """Create new workflow"""
        workflow = Workflow(
            id=uuid4(),
            name=name,
            state=WorkflowState.DRAFT,
            dag_definition=dag_definition
        )
        self.workflows[workflow.id] = workflow
        return workflow
    
    async def validate_workflow(self, workflow_id: UUID) -> Dict:
        """Validate workflow DAG for cycles"""
        workflow = self.workflows[workflow_id]
        
        resolver = DependencyResolver()
        
        # Build dependency graph from DAG
        nodes = workflow.dag_definition.get("nodes", [])
        edges = workflow.dag_definition.get("edges", [])
        
        # Build graph
        node_map = {node["id"]: node for node in nodes}
        for node_id in node_map.keys():
            dependencies = [
                e["source"] for e in edges if e["target"] == node_id
            ]
            resolver.add_task(node_id, dependencies)
        
        try:
            order = resolver.resolve_order()
            workflow.state = WorkflowState.READY
            return {"valid": True, "order": order}
        except ValueError as e:
            workflow.state = WorkflowState.DRAFT
            return {"valid": False, "error": str(e)}
    
    async def start_workflow(self, workflow_id: UUID):
        """Start workflow execution"""
        workflow = self.workflows[workflow_id]
        
        if workflow.state != WorkflowState.READY:
            raise ValueError(f"Workflow not ready: {workflow.state}")
        
        workflow.state = WorkflowState.RUNNING
        
        # Get execution order
        validation = await self.validate_workflow(workflow_id)
        execution_order = validation["order"]
        
        # Submit tasks in order
        for node_id in execution_order:
            node = next(n for n in workflow.dag_definition["nodes"] if n["id"] == node_id)
            
            task = await self.task_queue.add_task(
                name=node.get("name", node_id),
                required_capabilities=node.get("capabilities", []),
                priority=len(execution_order) - execution_order.index(node_id),  # Earlier tasks = higher priority
            )
            workflow.tasks.append(task.id)
        
        return workflow
```

**Validation**:
- Dependency resolution detects cycles
- Tasks ordered correctly
- Workflow executes in proper sequence
- Inter-agent messages delivered

**Checkpoint**: US3 Workflows complete ✓

---

## Success Criteria

- [ ] Tasks can be queued and prioritized
- [ ] Delegation daemon assigns tasks to agents with matching capabilities
- [ ] Dependency resolver detects cycles and orders tasks correctly
- [ ] Inter-agent messaging working for task results
- [ ] Workflows execute in correct dependency order
- [ ] Work-stealing balances load across idle agents

## Communication Protocol

After completing Phase 5:
```json
{
  "agent": "workflow-specialist",
  "phase": "phase_5_us3_complete",
  "tasks_completed": ["T084", ..., "T105"],
  "checkpoint_validated": true,
  "workflow_stats": {
    "tasks_queued": 100,
    "tasks_assigned": 50,
    "workflows_executed": 5
  }
}
```

**Priority**: P3 - Start after backend + integration engineer Phase 3 complete
