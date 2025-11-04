# DevOps Engineer - Implementation Instructions

## Mission
Set up infrastructure, configure environments, and prepare deployment infrastructure for the multi-agent framework.

## Context
- **Project**: fusion-kit multi-agent framework
- **Branch**: `001-multi-agent-framework`
- **Working Directory**: `/home/hyperuser/fusion-kit`
- **Role**: Infrastructure & Deployment

## Phase 1: Setup (T013-T014) - PARALLEL with backend

### Task: Initialize Workspace & Environment

**File**: `workspaces/.gitignore`

```
# Agent runtime workspaces
agent-*/
*.log
*.db
*.sqlite
.env.local
```

**File**: `.env.example`

```bash
# LLM Provider Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./fusion_kit.db

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Dashboard Configuration
DASHBOARD_PORT=3000
DASHBOARD_URL=http://localhost:3000

# Workspace Configuration
WORKSPACES_ROOT=./workspaces
WORKSPACE_PERMISSIONS=0o700

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Feature Flags
ENABLE_MULTI_AGENT=true
MAX_CONCURRENT_AGENTS=20

# Testing Configuration
TEST_DATABASE_URL=sqlite+aiosqlite:///:memory:
```

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=sqlite+aiosqlite:///./fusion_kit.db
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - ./src:/app/src
      - ./workspaces:/app/workspaces
    command: uvicorn fusion_kit.api.main:app --host 0.0.0.0 --port 8000 --reload

  dashboard:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend
    volumes:
      - ./dashboard/src:/app/src

volumes:
  redis_data:

networks:
  default:
    name: fusion-kit-network
```

**File**: `Dockerfile.backend`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY src ./src
COPY specs ./specs

EXPOSE 8000

CMD ["uvicorn", "fusion_kit.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**File**: `dashboard/Dockerfile`

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json .
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

**Validation**:
- .env.example has all required variables
- docker-compose.yml is valid
- Both Dockerfiles build successfully

**Checkpoint**: Infrastructure templates ready ✓

---

## Phase 8: Polish & Documentation (T148-T151, T163-T164)

### Documentation (T148-T151)

**File**: `docs/architecture.md`

```markdown
# Multi-Agent Orchestration Framework Architecture

## System Overview

```
┌──────────────────────────────────────────┐
│         User Interface                    │
│  (Web Dashboard / CLI / API)              │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│    API Layer (FastAPI)                   │
│  - Agent Management                      │
│  - Task Coordination                     │
│  - Workflow Orchestration                │
│  - WebSocket Events                      │
└──────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Core Layer   │ │Message Queue │ │  Database    │
│ - Agents     │ │  (Redis      │ │ (SQLite      │
│ - Workspace  │ │  Pub/Sub)    │ │ /PostgreSQL) │
│ - Lifecycle  │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
        │
        ▼
┌──────────────────────────────────────────┐
│    Provider System                       │
│  - OpenRouter (LLM Provider)             │
│  - Plugin Architecture                   │
│  - Capability Registry                   │
└──────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────┐
│    Agents (Isolated Workspaces)          │
│  - Agent 1 /workspaces/agent-uuid1/      │
│  - Agent 2 /workspaces/agent-uuid2/      │
│  - Agent N /workspaces/agent-uuidN/      │
└──────────────────────────────────────────┘
```

## Key Components

### 1. Core (src/fusion_kit/core/)
- **Agent**: Lifecycle management with state machine
- **Workspace**: Isolated filesystem per agent
- **AgentManager**: Spawn, pause, resume, terminate operations

### 2. Providers (src/fusion_kit/providers/)
- **LLMProvider**: Abstract interface for LLM backends
- **ProviderRegistry**: Plugin registration system
- **OpenRouter**: OpenRouter API implementation

### 3. Coordination (src/fusion_kit/coordination/)
- **TaskQueue**: Priority-based task queuing
- **DelegationDaemon**: Agent assignment based on capabilities
- **WorkflowEngine**: DAG-based workflow orchestration
- **DependencyResolver**: Topological sorting of dependencies

### 4. Messaging (src/fusion_kit/messaging/)
- **MessageQueue**: Redis pub/sub wrapper
- **MessageRouter**: Inter-agent message routing
- **Channels**: Topic management

### 5. Monitoring (src/fusion_kit/monitoring/)
- **EventLogger**: Event persistence
- **HealthMonitor**: Agent heartbeat tracking
- **MetricsCollector**: Resource usage tracking

### 6. Persistence (src/fusion_kit/persistence/)
- **Models**: 10 SQLAlchemy data entities
- **Repositories**: Async CRUD operations
- **Migrations**: Database schema versioning

### 7. API (src/fusion_kit/api/)
- **Agents**: Agent CRUD and lifecycle endpoints
- **Tasks**: Task management endpoints
- **Workflows**: Workflow orchestration endpoints
- **Events**: WebSocket event streaming
- **Health**: System health checks

## Data Flow

### Agent Spawning
1. User requests agent spawn via API
2. API calls DelegationDaemon
3. Daemon calls Provider to instantiate LLM
4. Provider returns agent handle
5. Core creates workspace directory
6. Agent saved to database
7. Event emitted: "agent.spawned"

### Task Execution
1. Task created and added to queue
2. DelegationDaemon polls for ready tasks
3. For each ready task, finds best agent
4. Assigns task to agent
5. Message published to agent topic
6. Agent processes task
7. Result published back via message queue
8. Dependent tasks become ready

### Workflow Orchestration
1. Workflow DAG defined with nodes and edges
2. Dependency resolver validates (detects cycles)
3. Tasks created in dependency order
4. Assigned to agents for parallel execution
5. Results aggregated and flow to dependents
6. Workflow completes when all tasks done

## Deployment Options

### Development (docker-compose)
```bash
docker-compose up
```

### Production (Kubernetes)
See k8s/ manifests for container orchestration

### Single Machine
Direct installation with systemd services
```
```

**File**: `docs/deployment.md`

```markdown
# Deployment Guide

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis 7+
- Docker (optional but recommended)

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up
```

This starts:
- Backend API on http://localhost:8000
- Dashboard on http://localhost:3000
- Redis on localhost:6379

### Option 2: Manual Setup

```bash
# Backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
uvicorn fusion_kit.api.main:app --reload

# Dashboard (new terminal)
cd dashboard
npm install
npm run dev

# Redis (new terminal)
redis-server
```

### Production Deployment

See `k8s/` directory for Kubernetes manifests.

#### Key Considerations
- Use PostgreSQL instead of SQLite
- Use Redis Cluster for pub/sub
- Enable authentication on all services
- Use TLS for all communication
- Implement proper backup strategy
- Monitor agent resource usage
```

**File**: `CHANGELOG.md` - Update with release notes

**File**: `README.md` - Add multi-agent framework section

### Deployment Scripts (T163)

**File**: `scripts/deploy.sh`

```bash
#!/bin/bash
set -e

echo "🚀 Deploying Fusion Kit Multi-Agent Framework"

# Build backend
echo "Building backend..."
docker build -t fusion-kit-backend:latest -f Dockerfile.backend .

# Build dashboard
echo "Building dashboard..."
docker build -t fusion-kit-dashboard:latest dashboard/

# Push to registry (if configured)
if [ ! -z "$REGISTRY" ]; then
  docker push fusion-kit-backend:latest
  docker push fusion-kit-dashboard:latest
fi

# Deploy
if [ "$ENVIRONMENT" = "kubernetes" ]; then
  kubectl apply -f k8s/
  kubectl rollout status deployment/fusion-kit-backend
else
  docker-compose up -d
fi

echo "✅ Deployment complete"
```

**File**: `scripts/health-check.sh`

```bash
#!/bin/bash

echo "🏥 Health Check"

# Check API
API_STATUS=$(curl -s http://localhost:8000/api/v1/health || echo "error")
echo "API: $API_STATUS"

# Check Redis
REDIS_STATUS=$(redis-cli ping 2>/dev/null || echo "error")
echo "Redis: $REDIS_STATUS"

# Check Database
DB_STATUS=$(sqlite3 fusion_kit.db "SELECT 1;" 2>/dev/null || echo "error")
echo "Database: $DB_STATUS"

# Check Dashboard
DASHBOARD_STATUS=$(curl -s http://localhost:3000/ | head -c 20)
echo "Dashboard: ${DASHBOARD_STATUS:0:20}..."
```

### Update CHANGELOG (T164)

**File**: `CHANGELOG.md`

```markdown
## [1.0.0] - 2025-11-04

### Added
- Multi-agent orchestration framework
  - Agent spawning with isolated workspaces
  - Task coordination with dependency resolution
  - Real-time monitoring dashboard
  - Workflow visualization and editing
  - Inter-agent messaging via Redis pub/sub
  - OpenRouter provider integration
  - Plugin architecture for LLM providers

- Database models for 10 entities
- FastAPI REST API with 25+ endpoints
- React real-time dashboard with WebSocket
- CLI commands for agent management
- Comprehensive testing suite
- Docker and Kubernetes deployment configs

### Backward Compatibility
- 100% compatible with existing specify CLI
- All existing agent configurations supported
- <5% performance overhead in single-agent mode

### Tech Stack
- Backend: Python 3.11, FastAPI, SQLAlchemy, Redis
- Frontend: React 18, Vite, React Flow, Chart.js
- Database: SQLite (dev), PostgreSQL (prod)
```

---

## Success Criteria

- [ ] docker-compose.yml valid and tested
- [ ] All Dockerfiles build successfully
- [ ] .env.example has all required variables
- [ ] Documentation complete and clear
- [ ] Deployment scripts working
- [ ] Health check script functional

## Communication Protocol

After Phase 8:
```json
{
  "agent": "devops-engineer",
  "phase": "phase_8_complete",
  "infrastructure": {
    "docker_compose": "valid",
    "dockerfiles": "built",
    "documentation": "complete",
    "deployment_ready": true
  },
  "checkpoint_validated": true
}
```

**Priority**: P4 - Infrastructure and operations, parallel with other work
