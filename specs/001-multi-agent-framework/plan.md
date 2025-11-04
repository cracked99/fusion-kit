# Implementation Plan: Multi-Agent Orchestration Framework

**Branch**: `001-multi-agent-framework` | **Date**: 2025-11-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-multi-agent-framework/spec.md`

**Note**: This plan follows the `/speckit.plan` workflow with Phase 0 research and Phase 1 design artifacts.

## Summary

Transform fusion-kit from a single-agent CLI tool into an extensible multi-agent orchestration platform. The system will support spawning multiple AI agents with isolated workspaces, coordinating collaborative workflows through message-based communication, and monitoring agent activity through a real-time web dashboard. Key technical approach: Python 3.11+ backend with FastAPI for APIs, Redis for message queue, SQLite for persistence, React for dashboard, and extensible LLM provider architecture starting with OpenRouter integration. Maintains full backward compatibility with existing fusion-kit CLI functionality.

## Technical Context

**Language/Version**: Python 3.11+ (existing fusion-kit requirement)  
**Primary Dependencies**: 
- **Backend Core**: FastAPI (async web framework), Pydantic (data validation)
- **Message Queue**: Redis with redis-py (pub/sub + persistence)
- **Database**: SQLite with sqlalchemy (agent state, events, workflows)
- **LLM Integration**: httpx (async HTTP for provider APIs), tenacity (retry logic)
- **Dashboard Backend**: FastAPI WebSockets (real-time streaming)
- **Dashboard Frontend**: React 18, React Flow (node editor), Socket.IO client, Chart.js
- **CLI**: Typer, Rich (preserve existing fusion-kit stack)
- **Testing**: pytest, pytest-asyncio, httpx mock

**Storage**: 
- SQLite for agent state, event logs, workflow definitions, task history
- Filesystem for isolated agent workspaces (directory per agent)
- Redis for message queue and ephemeral pub/sub channels

**Testing**: pytest with async support, contract tests for provider APIs, integration tests for multi-agent workflows  
**Target Platform**: Linux/macOS/WSL2 (existing fusion-kit support), single-machine deployment  
**Project Type**: Web application (backend APIs + frontend dashboard) with CLI integration  
**Performance Goals**: 
- Agent spawning < 10 seconds (SC-008)
- Task assignment < 5 seconds (SC-004)
- Dashboard updates < 2 seconds latency (SC-010)
- Support 10-20 concurrent agents (SC-003)

**Constraints**: 
- Must maintain 100% backward compatibility with existing CLI (SC-016, SC-017)
- < 5% performance overhead for single-agent mode (SC-018)
- 99.9% agent lifecycle reliability (SC-001)
- Filesystem-based workspace isolation for MVP (container support deferred)

**Scale/Scope**: 
- MVP: 10-20 concurrent agents on single machine
- Task graphs up to 50 nodes, 100 dependencies (SC-006)
- Support 10k+ events logged per session
- Dashboard responsive with 20 agents (SC-011)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Specification-First Development ✅
- **Status**: PASS
- **Evidence**: Complete technology-agnostic specification with 42 functional requirements, 21 success criteria, and 5 prioritized user stories. All "what/why" defined before "how".

### II. AI-Agent Agnostic Design ✅
- **Status**: PASS  
- **Evidence**: Multi-agent framework maintains compatibility with all existing agent types (claude, gemini, droid, etc.) per FR-034. Template structures unchanged (FR-035). Provider architecture extensible beyond OpenRouter.

### III. Iterative Refinement Over One-Shot Generation ✅
- **Status**: PASS
- **Evidence**: Following specify → clarify → plan → tasks → implement workflow. Two clarifications resolved before planning. Plan phase active now.

### IV. Template-Driven Consistency ✅
- **Status**: PASS
- **Evidence**: Using standard spec-template.md, plan-template.md structure. All mandatory sections completed with proper formatting.

### V. Independent Testability ✅
- **Status**: PASS
- **Evidence**: 5 user stories with independent test criteria. Each story deliverable as standalone MVP (P1 agent management, P2 monitoring, P3 workflows, P4 visualization, P1 compatibility).

### Quality & Testing Standards ✅
- **Status**: PASS
- **Evidence**: All requirements testable and measurable. Success criteria technology-agnostic. Zero [NEEDS CLARIFICATION] markers remaining. Assumptions documented.

### Validation Gates ✅
- **Status**: PASS
- **Evidence**: Specification validated via requirements checklist. Constitution check performed before planning. Task validation will occur in Phase 2.

**Overall**: ✅ **PASS** - No constitutional violations. Ready to proceed with Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── specify_cli/              # Existing CLI (preserve compatibility)
│   ├── __init__.py
│   ├── commands/
│   └── utils/
├── fusion_kit/               # NEW: Multi-agent framework
│   ├── core/                 # Agent lifecycle, workspace management
│   │   ├── agent.py
│   │   ├── workspace.py
│   │   ├── lifecycle.py
│   │   └── capability_registry.py
│   ├── providers/            # LLM provider integrations
│   │   ├── base.py          # Abstract provider interface
│   │   ├── openrouter.py    # OpenRouter implementation
│   │   └── registry.py      # Provider plugin system
│   ├── coordination/         # Task management and delegation
│   │   ├── task_queue.py
│   │   ├── delegation_daemon.py
│   │   ├── dependency_resolver.py
│   │   └── workflow_engine.py
│   ├── messaging/            # Inter-agent communication
│   │   ├── message_queue.py  # Redis pub/sub wrapper
│   │   ├── message.py        # Message models
│   │   └── channels.py       # Topic/channel management
│   ├── monitoring/           # Observability and metrics
│   │   ├── event_logger.py
│   │   ├── metrics_collector.py
│   │   └── health_monitor.py
│   ├── persistence/          # Data storage
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── repositories.py   # Data access layer
│   │   └── migrations/
│   ├── api/                  # FastAPI backend
│   │   ├── main.py
│   │   ├── agents.py         # Agent management endpoints
│   │   ├── tasks.py          # Task coordination endpoints
│   │   ├── workflows.py      # Workflow management endpoints
│   │   ├── events.py         # Event streaming WebSocket
│   │   └── schemas.py        # Pydantic request/response models
│   └── cli/                  # Multi-agent CLI commands
│       ├── agent_cmd.py
│       ├── workflow_cmd.py
│       └── dashboard_cmd.py

dashboard/                    # React frontend
├── src/
│   ├── components/
│   │   ├── AgentCard.tsx
│   │   ├── WorkflowEditor.tsx
│   │   ├── EventLog.tsx
│   │   └── MetricsDashboard.tsx
│   ├── pages/
│   │   ├── Overview.tsx
│   │   ├── Agents.tsx
│   │   ├── Workflows.tsx
│   │   └── Monitoring.tsx
│   ├── services/
│   │   ├── api.ts           # HTTP API client
│   │   ├── websocket.ts     # Real-time event stream
│   │   └── state.ts         # State management
│   └── App.tsx
├── public/
└── package.json

tests/
├── unit/                     # Unit tests for components
│   ├── test_agent.py
│   ├── test_providers.py
│   ├── test_messaging.py
│   └── test_coordination.py
├── integration/              # Multi-agent workflow tests
│   ├── test_agent_spawning.py
│   ├── test_workflows.py
│   └── test_message_passing.py
└── contract/                 # Provider API contract tests
    ├── test_openrouter.py
    └── test_provider_interface.py

workspaces/                   # Agent workspace root (git ignore)
└── agent-{uuid}/            # Per-agent isolated directories
```

**Structure Decision**: Web application architecture selected. Backend extends existing `src/` with new `fusion_kit/` package to maintain CLI compatibility. Dashboard is standalone React SPA. Agent workspaces isolated in dedicated `workspaces/` directory outside source tree.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations - all constitutional principles satisfied. No complexity justification required.
