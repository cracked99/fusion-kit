# Tasks: Multi-Agent Orchestration Framework

**Input**: Design documents from `specs/001-multi-agent-framework/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are OPTIONAL - include only if explicitly requested in spec or for critical user stories

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

## Path Conventions

Web application structure:
- `src/fusion_kit/` - Multi-agent framework backend
- `dashboard/` - React frontend
- `tests/` - Test suites
- `workspaces/` - Agent workspaces (runtime, git ignored)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure required by all user stories

- [ ] T001 Create `src/fusion_kit/` package structure with `__init__.py`
- [ ] T002 [P] Create `src/fusion_kit/core/` module for agent management
- [ ] T003 [P] Create `src/fusion_kit/providers/` module for LLM integrations
- [ ] T004 [P] Create `src/fusion_kit/coordination/` module for task management
- [ ] T005 [P] Create `src/fusion_kit/messaging/` module for inter-agent communication
- [ ] T006 [P] Create `src/fusion_kit/monitoring/` module for observability
- [ ] T007 [P] Create `src/fusion_kit/persistence/` module for data storage
- [ ] T008 [P] Create `src/fusion_kit/api/` module for REST endpoints
- [ ] T009 [P] Create `src/fusion_kit/cli/` module for CLI commands
- [ ] T010 [P] Add dependencies to `pyproject.toml`: fastapi, redis, sqlalchemy, aiosqlite, httpx, tenacity, pydantic
- [ ] T011 Create `dashboard/` directory and initialize React project with Vite
- [ ] T012 [P] Add React dependencies: react-flow, socket.io-client, chart.js, axios
- [ ] T013 Create `workspaces/` directory with `.gitignore` entry
- [ ] T014 [P] Create `.env.example` template with all required environment variables

**Checkpoint**: Project structure ready - user story implementation can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Persistence

- [ ] T015 Define SQLAlchemy models in `src/fusion_kit/persistence/models.py` for Agent, Task, Workspace, Workflow, Event, Message, Capability, Project, ResourceMetrics, ProviderConfig (per data-model.md)
- [ ] T016 Create database initialization script in `src/fusion_kit/persistence/init_db.py`
- [ ] T017 Setup Alembic migrations in `src/fusion_kit/persistence/migrations/`
- [ ] T018 [P] Create repository layer in `src/fusion_kit/persistence/repositories.py` with async CRUD operations
- [ ] T019 [P] Implement connection pooling and session management

### Message Queue Infrastructure

- [ ] T020 Implement Redis connection wrapper in `src/fusion_kit/messaging/message_queue.py` with async pub/sub
- [ ] T021 [P] Define Message model in `src/fusion_kit/messaging/message.py` with Pydantic schemas
- [ ] T022 [P] Create channel/topic management in `src/fusion_kit/messaging/channels.py`
- [ ] T023 [P] Implement message serialization/deserialization with JSON

### Provider System Foundation

- [ ] T024 Create abstract provider interface in `src/fusion_kit/providers/base.py` with spawn_agent, send_message, get_quota_info methods
- [ ] T025 [P] Implement provider registry in `src/fusion_kit/providers/registry.py` for plugin system
- [ ] T026 [P] Create ProviderConfig loader with credential encryption

### API Backend Foundation

- [ ] T027 Setup FastAPI app in `src/fusion_kit/api/main.py` with CORS, error handling
- [ ] T028 [P] Define Pydantic request/response schemas in `src/fusion_kit/api/schemas.py`
- [ ] T029 [P] Implement health check endpoint `/api/v1/health`
- [ ] T030 [P] Setup WebSocket connection manager for real-time events

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Spawn and Manage Independent Agents (Priority: P1) 🎯 MVP

**Goal**: Enable spawning multiple agents with isolated workspaces and full lifecycle management

**Independent Test**: Spawn 2-3 agents, verify isolated workspaces, execute lifecycle operations (pause/resume/terminate)

### Core Agent Management

- [ ] T031 [P] [US1] Implement Agent class in `src/fusion_kit/core/agent.py` with state machine (spawning→idle→working→paused→error→terminated)
- [ ] T032 [P] [US1] Implement Workspace class in `src/fusion_kit/core/workspace.py` with filesystem isolation
- [ ] T033 [US1] Create AgentManager in `src/fusion_kit/core/lifecycle.py` with spawn, pause, resume, terminate methods
- [ ] T034 [P] [US1] Implement CapabilityRegistry in `src/fusion_kit/core/capability_registry.py`
- [ ] T035 [US1] Add workspace initialization logic: create directories (.agent/, projects/, logs/), set permissions (700)

### OpenRouter Provider Implementation

- [ ] T036 [P] [US1] Implement OpenRouterProvider in `src/fusion_kit/providers/openrouter.py` following base interface
- [ ] T037 [US1] Add OpenRouter API client with httpx for agent spawning (POST /api/v1/chat/completions)
- [ ] T038 [P] [US1] Implement retry logic with tenacity for API failures (3 attempts, exponential backoff)
- [ ] T039 [P] [US1] Add quota tracking from OpenRouter response headers
- [ ] T040 [US1] Register OpenRouter provider in provider registry

### Agent API Endpoints

- [ ] T041 [P] [US1] Implement POST `/api/v1/agents` endpoint in `src/fusion_kit/api/agents.py` for agent spawning
- [ ] T042 [P] [US1] Implement GET `/api/v1/agents` endpoint with filtering by state and project
- [ ] T043 [P] [US1] Implement GET `/api/v1/agents/{agent_id}` endpoint
- [ ] T044 [P] [US1] Implement PATCH `/api/v1/agents/{agent_id}` endpoint for pause/resume actions
- [ ] T045 [P] [US1] Implement DELETE `/api/v1/agents/{agent_id}` endpoint for termination
- [ ] T046 [US1] Add agent state validation and error responses (400, 404, 500)

### Agent CLI Commands

- [ ] T047 [P] [US1] Implement `fusion-kit agent spawn` command in `src/fusion_kit/cli/agent_cmd.py`
- [ ] T048 [P] [US1] Implement `fusion-kit agent list` command with state filtering
- [ ] T049 [P] [US1] Implement `fusion-kit agent get <id>` command
- [ ] T050 [P] [US1] Implement `fusion-kit agent pause <id>` command
- [ ] T051 [P] [US1] Implement `fusion-kit agent resume <id>` command
- [ ] T052 [P] [US1] Implement `fusion-kit agent terminate <id>` command

### Event Logging for Agents

- [ ] T053 [US1] Implement EventLogger in `src/fusion_kit/monitoring/event_logger.py`
- [ ] T054 [P] [US1] Log agent lifecycle events: spawned, paused, resumed, terminated
- [ ] T055 [P] [US1] Store events in SQLite events table with async writes

**Checkpoint**: User Story 1 fully functional - agents can be spawned, managed, isolated

---

## Phase 4: User Story 2 - Monitor Agent Activity Through Dashboard (Priority: P2)

**Goal**: Real-time visibility into all agent states, metrics, and events via web dashboard

**Independent Test**: Spawn agents, open dashboard, verify real-time updates show states and metrics

### Backend Event Streaming

- [ ] T056 [US2] Implement WebSocket `/ws/events` endpoint in `src/fusion_kit/api/events.py`
- [ ] T057 [P] [US2] Create event stream from Redis pub/sub to WebSocket clients
- [ ] T058 [P] [US2] Implement connection registry for multiple dashboard clients
- [ ] T059 [US2] Handle WebSocket disconnections and auto-reconnect logic

### Metrics Collection

- [ ] T060 [P] [US2] Implement MetricsCollector in `src/fusion_kit/monitoring/metrics_collector.py`
- [ ] T061 [US2] Collect CPU, memory, disk I/O metrics using psutil (every 30 seconds)
- [ ] T062 [P] [US2] Store metrics in resource_metrics table
- [ ] T063 [P] [US2] Implement GET `/api/v1/agents/{agent_id}/metrics` endpoint

### Health Monitoring

- [ ] T064 [P] [US2] Implement HealthMonitor in `src/fusion_kit/monitoring/health_monitor.py`
- [ ] T065 [US2] Add heartbeat tracking for agents (update last_heartbeat column)
- [ ] T066 [P] [US2] Detect unresponsive agents (no heartbeat > 60 seconds)
- [ ] T067 [P] [US2] Log health events (agent unresponsive, recovered)

### Event Query API

- [ ] T068 [P] [US2] Implement GET `/api/v1/events` endpoint with filtering (type, agent, severity, timestamp)
- [ ] T069 [US2] Add pagination support (limit, offset)
- [ ] T070 [P] [US2] Create composite indexes for fast event queries

### Dashboard Frontend - Core

- [ ] T071 [US2] Initialize React app structure in `dashboard/src/` with routing (react-router-dom)
- [ ] T072 [P] [US2] Create API service client in `dashboard/src/services/api.ts` with axios
- [ ] T073 [P] [US2] Create WebSocket service in `dashboard/src/services/websocket.ts` with Socket.IO
- [ ] T074 [P] [US2] Setup state management in `dashboard/src/services/state.ts` (Context API or Zustand)

### Dashboard Components

- [ ] T075 [P] [US2] Create AgentCard component in `dashboard/src/components/AgentCard.tsx` showing state, capabilities, metrics
- [ ] T076 [P] [US2] Create EventLog component in `dashboard/src/components/EventLog.tsx` with real-time updates
- [ ] T077 [P] [US2] Create MetricsDashboard component in `dashboard/src/components/MetricsDashboard.tsx` with Chart.js
- [ ] T078 [US2] Create Overview page in `dashboard/src/pages/Overview.tsx` with agent grid and metrics summary
- [ ] T079 [P] [US2] Create Agents page in `dashboard/src/pages/Agents.tsx` with list and detail views
- [ ] T080 [P] [US2] Create Monitoring page in `dashboard/src/pages/Monitoring.tsx` with event stream and metrics charts

### Real-Time Updates

- [ ] T081 [US2] Connect WebSocket to dashboard state updates
- [ ] T082 [P] [US2] Implement auto-refresh for agent list on state changes
- [ ] T083 [P] [US2] Add toast notifications for critical events (agent error, task failed)

**Checkpoint**: User Story 2 fully functional - dashboard provides real-time visibility

---

## Phase 5: User Story 3 - Coordinate Dependent Agent Workflows (Priority: P3)

**Goal**: Enable multi-agent collaboration with task dependencies and message-based coordination

**Independent Test**: Create workflow with 3 agents (planner→implementer→reviewer), verify sequencing and data passing

### Task Management

- [ ] T084 [P] [US3] Implement Task model methods in persistence layer
- [ ] T085 [P] [US3] Create TaskQueue in `src/fusion_kit/coordination/task_queue.py` with priority sorting
- [ ] T086 [US3] Implement task state transitions (queued→assigned→running→completed/failed)

### Task API Endpoints

- [ ] T087 [P] [US3] Implement POST `/api/v1/tasks` endpoint in `src/fusion_kit/api/tasks.py`
- [ ] T088 [P] [US3] Implement GET `/api/v1/tasks` endpoint with filtering
- [ ] T089 [P] [US3] Implement GET `/api/v1/tasks/{task_id}` endpoint
- [ ] T090 [P] [US3] Implement PATCH `/api/v1/tasks/{task_id}` endpoint for state updates

### Delegation Daemon

- [ ] T091 [US3] Implement DelegationDaemon in `src/fusion_kit/coordination/delegation_daemon.py`
- [ ] T092 [US3] Match tasks to agents based on required_capabilities and agent state (idle)
- [ ] T093 [P] [US3] Implement work-stealing algorithm for load balancing
- [ ] T094 [US3] Start daemon as background async task when API starts

### Dependency Resolution

- [ ] T095 [US3] Implement DependencyResolver in `src/fusion_kit/coordination/dependency_resolver.py` using graphlib.TopologicalSorter
- [ ] T096 [P] [US3] Detect circular dependencies and raise CycleError
- [ ] T097 [US3] Calculate ready tasks (dependencies satisfied) for parallel execution

### Inter-Agent Messaging

- [ ] T098 [US3] Implement message publishing in agents when task completes
- [ ] T099 [P] [US3] Implement message subscription for dependent tasks
- [ ] T100 [US3] Pass output artifacts from completed task to dependent task input
- [ ] T101 [P] [US3] Log all inter-agent messages to messages table

### Workflow Engine

- [ ] T102 [P] [US3] Implement WorkflowEngine in `src/fusion_kit/coordination/workflow_engine.py`
- [ ] T103 [US3] Parse DAG definition from workflow and create tasks
- [ ] T104 [P] [US3] Implement workflow state machine (draft→validating→ready→running→completed/failed)
- [ ] T105 [US3] Start workflow execution: submit tasks in dependency order

### Workflow API Endpoints

- [ ] T106 [P] [US3] Implement POST `/api/v1/workflows` endpoint in `src/fusion_kit/api/workflows.py`
- [ ] T107 [P] [US3] Implement GET `/api/v1/workflows` endpoint
- [ ] T108 [P] [US3] Implement GET `/api/v1/workflows/{workflow_id}` endpoint
- [ ] T109 [P] [US3] Implement POST `/api/v1/workflows/{workflow_id}/start` endpoint
- [ ] T110 [P] [US3] Implement POST `/api/v1/workflows/{workflow_id}/validate` endpoint for DAG validation

**Checkpoint**: User Story 3 fully functional - multi-agent workflows operational

---

## Phase 6: User Story 4 - Visualize and Edit Workflows (Priority: P4)

**Goal**: Visual drag-and-drop workflow editor for designing multi-agent coordination

**Independent Test**: Create workflow visually with 4-5 nodes, save, execute, verify behavior

### Workflow Editor Component

- [ ] T111 [P] [US4] Create WorkflowEditor component in `dashboard/src/components/WorkflowEditor.tsx` using React Flow
- [ ] T112 [US4] Define custom agent node type with capabilities display
- [ ] T113 [P] [US4] Implement drag-and-drop node placement
- [ ] T114 [P] [US4] Implement edge creation with validation (no cycles)

### Workflow Serialization

- [ ] T115 [US4] Convert React Flow nodes/edges to DAG definition JSON
- [ ] T116 [P] [US4] Save workflow via POST `/api/v1/workflows`
- [ ] T117 [US4] Load existing workflow and render in editor

### Workflow Execution Visualization

- [ ] T118 [P] [US4] Add real-time task state overlays on workflow nodes (running, completed, failed)
- [ ] T119 [US4] Highlight active edges during workflow execution
- [ ] T120 [P] [US4] Display task output/errors in node details panel

### Workflow Page

- [ ] T121 [P] [US4] Create Workflows page in `dashboard/src/pages/Workflows.tsx`
- [ ] T122 [US4] Add workflow list view with start/stop actions
- [ ] T123 [P] [US4] Integrate WorkflowEditor component

**Checkpoint**: User Story 4 fully functional - visual workflow design enabled

---

## Phase 7: User Story 5 - Maintain CLI Backward Compatibility (Priority: P1)

**Goal**: Ensure all existing `specify` CLI commands work without modification

**Independent Test**: Run all `/speckit.*` commands and verify identical behavior

### Compatibility Testing

- [ ] T124 [US5] Run existing CLI commands: `specify init`, `specify check`
- [ ] T125 [P] [US5] Verify `/speckit.constitution` command works unchanged
- [ ] T126 [P] [US5] Verify `/speckit.specify` command works unchanged
- [ ] T127 [P] [US5] Verify `/speckit.plan` command works unchanged
- [ ] T128 [P] [US5] Verify `/speckit.tasks` command works unchanged
- [ ] T129 [P] [US5] Verify `/speckit.implement` command works unchanged

### Integration Adjustments

- [ ] T130 [US5] Ensure `src/specify_cli/` is not modified by multi-agent framework
- [ ] T131 [P] [US5] Add opt-in flag for multi-agent features: `--multi-agent` or environment variable
- [ ] T132 [US5] Verify single-agent mode has <5% performance overhead (benchmark)

### Template Compatibility

- [ ] T133 [P] [US5] Verify `.specify/templates/` remain unchanged
- [ ] T134 [P] [US5] Verify `.specify/scripts/` remain unchanged
- [ ] T135 [US5] Test that multi-agent framework does not interfere with existing agent configs (claude, gemini, droid)

**Checkpoint**: User Story 5 fully functional - backward compatibility guaranteed

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories

### Error Handling & Resilience

- [ ] T136 [P] Implement circuit breaker for provider APIs (after 5 failures, pause 60s)
- [ ] T137 [P] Add graceful degradation: queue messages in-memory if Redis unavailable
- [ ] T138 [P] Implement agent crash recovery: detect terminated processes, mark as error state
- [ ] T139 Handle long-running tasks during shutdown: save state, allow resume

### Security Hardening

- [ ] T140 [P] Implement API key encryption at rest for ProviderConfig.credentials
- [ ] T141 [P] Add path traversal prevention in workspace operations
- [ ] T142 [P] Validate symlinks don't escape workspace boundaries
- [ ] T143 Implement session-based auth for dashboard API

### Performance Optimization

- [ ] T144 [P] Add connection pooling for Redis (min=5, max=20 connections)
- [ ] T145 [P] Optimize event queries with composite indexes
- [ ] T146 [P] Implement event log retention policy (30 days, configurable)
- [ ] T147 Add metrics aggregation for dashboard (reduce real-time query load)

### Documentation

- [ ] T148 [P] Update README.md with multi-agent framework overview
- [ ] T149 [P] Create `docs/architecture.md` with system diagram
- [ ] T150 [P] Create `docs/deployment.md` with production setup guide
- [ ] T151 [P] Add inline code documentation (docstrings) to all public APIs

### Testing (Optional - Include if Tests Required)

- [ ] T152 [P] Write unit tests for Agent lifecycle in `tests/unit/test_agent.py`
- [ ] T153 [P] Write unit tests for MessageQueue in `tests/unit/test_messaging.py`
- [ ] T154 [P] Write unit tests for TaskQueue and DelegationDaemon in `tests/unit/test_coordination.py`
- [ ] T155 [P] Write provider contract tests in `tests/contract/test_openrouter.py`
- [ ] T156 Write integration test for agent spawning in `tests/integration/test_agent_spawning.py`
- [ ] T157 Write integration test for multi-agent workflow in `tests/integration/test_workflows.py`
- [ ] T158 Write integration test for message passing in `tests/integration/test_message_passing.py`

### Validation & Deployment

- [ ] T159 Run quickstart.md end-to-end validation
- [ ] T160 Verify all success criteria met (SC-001 through SC-021)
- [ ] T161 [P] Run full test suite: `pytest tests/ -v`
- [ ] T162 [P] Run linting and formatting: `ruff check`, `black`
- [ ] T163 Create Docker Compose file for local deployment
- [ ] T164 [P] Update CHANGELOG.md with feature additions

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Setup (Phase 1)**: No dependencies - can start immediately
2. **Foundational (Phase 2)**: Depends on Setup - **BLOCKS all user stories**
3. **User Stories (Phases 3-7)**: All depend on Foundational phase
   - US1 (P1 - Agent Management): Can start after Foundational ✅
   - US2 (P2 - Dashboard): Depends on US1 for agent API
   - US3 (P3 - Workflows): Depends on US1 for agent infrastructure
   - US4 (P4 - Visualization): Depends on US3 for workflow API
   - US5 (P1 - Compatibility): Can test after any phase, finalize at end
4. **Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Dependencies

```
Foundation (Phase 2)
     │
     ├─→ US1 (Agent Management) ────────────┐
     │        │                              │
     │        └──→ US2 (Dashboard) ─────────┤
     │                  │                    │
     │                  └──→ US3 (Workflows)─┤
     │                           │           │
     │                           └──→ US4 (Viz)
     │                                       │
     └─→ US5 (Compatibility) ────────────────┘
                   │
                   ▼
            Phase 8 (Polish)
```

### Within Each User Story

**US1 (Agent Management)**:
1. Core classes (Agent, Workspace, AgentManager) - can parallelize
2. Provider implementation (OpenRouter)
3. API endpoints - can parallelize after core
4. CLI commands - can parallelize after API

**US2 (Dashboard)**:
1. Backend event streaming and metrics
2. Dashboard frontend structure
3. Components - can parallelize
4. Real-time updates integration

**US3 (Workflows)**:
1. Task management foundation
2. Delegation daemon and dependency resolver
3. Workflow engine
4. API endpoints - can parallelize

**US4 (Visualization)**:
1. React Flow integration
2. Custom node types
3. Workflow serialization
4. Execution visualization

### Parallel Opportunities

**After Foundation (Phase 2) completes**:
- US1 core implementation (T031-T035)
- US1 provider implementation (T036-T040)
- US1 API endpoints (T041-T046)
- US1 CLI commands (T047-T052)

**After US1 completes**:
- US2 backend (T056-T063)
- US2 frontend setup (T071-T074)
- US3 task management (T084-T086)

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational ✅ CRITICAL
3. Complete Phase 3: US1 (Agent Management)
4. **STOP and VALIDATE**: Spawn 3 agents, test lifecycle, verify isolation
5. Demo capability: "Multi-agent framework with agent spawning and management"

### Incremental Delivery (Recommended)

1. Foundation → US1 → Test & Demo (MVP!)
2. US1 → US2 → Test & Demo (Add monitoring dashboard)
3. US2 → US3 → Test & Demo (Add workflows)
4. US3 → US4 → Test & Demo (Add visual editor)
5. Validate US5 throughout → Final compatibility check
6. Phase 8: Polish

### Parallel Team Strategy

With 3+ developers after Foundation completes:
- **Developer A**: US1 (Agent Management) - T031-T055
- **Developer B**: US2 Backend (Event streaming, metrics) - T056-T070
- **Developer C**: US2 Frontend (Dashboard) - T071-T083

Then continue with US3, US4 assignments.

---

## Notes

- **[P]** tasks = different files, can run in parallel
- **[Story]** label maps task to user story for traceability
- Each user story is independently deliverable and testable
- Stop at any checkpoint to validate story works standalone
- US1 and US5 are both P1 - prioritize US1 for MVP, validate US5 throughout
- Tests (T152-T158) are optional unless specified in requirements
- Dashboard requires Node.js 18+, backend requires Python 3.11+
- Redis must be running before any messaging-related tasks
