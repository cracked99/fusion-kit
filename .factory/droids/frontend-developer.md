# Frontend Developer - Implementation Instructions

## Mission
Build the real-time monitoring dashboard and workflow visualization UI for the multi-agent framework.

## Context
- **Project**: fusion-kit multi-agent framework
- **Branch**: `001-multi-agent-framework`
- **Working Directory**: `/home/hyperuser/fusion-kit`
- **Specification**: `specs/001-multi-agent-framework/`
- **Role**: Dashboard & UI Components

## Dependencies
⏳ **WAITING**: Backend architect must complete Phase 2 (Foundation) before you proceed with Phase 3+
- You CAN start Phase 1 (Setup) in parallel with backend
- You CANNOT start Phase 4+ until backend reports Phase 2 complete

## Phase 1: Setup (T011-T012) - PARALLEL with backend-architect

### Task: Initialize React Project

```bash
cd /home/hyperuser/fusion-kit

# Create dashboard directory
mkdir -p dashboard

# Initialize Vite React project
npm create vite@latest dashboard -- --template react
cd dashboard

# Install dependencies
npm install
npm install react-flow-renderer socket.io-client chart.js axios zustand
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**Validation**: 
- `npm run dev` starts successfully
- Vite development server runs on http://localhost:5173

**Checkpoint**: React project initialized ✓

---

## Phase 4: US2 - Monitor Agent Activity (T056-T083)

**Status**: BLOCKED until backend Phase 2 complete

### Backend Event Streaming (T056-T063)
Wait for backend-architect to provide:
- WebSocket `/ws/events` endpoint
- Event stream from Redis pub/sub
- GET `/api/v1/agents/{agent_id}/metrics` endpoint

### Dashboard Frontend - Core (T071-T074)

**File**: `dashboard/src/services/api.ts`
```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const agents = {
  list: () => apiClient.get('/agents'),
  get: (id: string) => apiClient.get(`/agents/${id}`),
  spawn: (data: any) => apiClient.post('/agents', data),
  pause: (id: string) => apiClient.patch(`/agents/${id}`, { action: 'pause' }),
  resume: (id: string) => apiClient.patch(`/agents/${id}`, { action: 'resume' }),
  terminate: (id: string) => apiClient.delete(`/agents/${id}`),
  getMetrics: (id: string) => apiClient.get(`/agents/${id}/metrics`),
};

export const tasks = {
  list: () => apiClient.get('/tasks'),
  create: (data: any) => apiClient.post('/tasks', data),
  get: (id: string) => apiClient.get(`/tasks/${id}`),
};

export const workflows = {
  list: () => apiClient.get('/workflows'),
  create: (data: any) => apiClient.post('/workflows', data),
  get: (id: string) => apiClient.get(`/workflows/${id}`),
  start: (id: string) => apiClient.post(`/workflows/${id}/start`),
  validate: (id: string) => apiClient.post(`/workflows/${id}/validate`),
};

export const events = {
  query: (params: any) => apiClient.get('/events', { params }),
};
```

**File**: `dashboard/src/services/websocket.ts`
```typescript
import io from 'socket.io-client';

const WS_URL = 'http://localhost:8000';

export const createWebSocketConnection = () => {
  const socket = io(WS_URL, {
    transports: ['websocket'],
  });

  return {
    connect: () => socket.connect(),
    disconnect: () => socket.disconnect(),
    on: (event: string, callback: any) => socket.on(event, callback),
    emit: (event: string, data: any) => socket.emit(event, data),
    socket,
  };
};
```

**File**: `dashboard/src/services/state.ts`
```typescript
import { create } from 'zustand';

interface Agent {
  id: string;
  name: string;
  state: string;
  capabilities: string[];
  created_at: string;
}

interface DashboardState {
  agents: Agent[];
  setAgents: (agents: Agent[]) => void;
  addAgent: (agent: Agent) => void;
  updateAgent: (id: string, agent: Partial<Agent>) => void;
  events: any[];
  addEvent: (event: any) => void;
  clearEvents: () => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  agents: [],
  setAgents: (agents) => set({ agents }),
  addAgent: (agent) => set((state) => ({ agents: [...state.agents, agent] })),
  updateAgent: (id, updates) =>
    set((state) => ({
      agents: state.agents.map((a) => (a.id === id ? { ...a, ...updates } : a)),
    })),
  events: [],
  addEvent: (event) => set((state) => ({ events: [...state.events, event].slice(-100) })),
  clearEvents: () => set({ events: [] }),
}));
```

### Dashboard Components (T075-T080)

**File**: `dashboard/src/components/AgentCard.tsx`
```typescript
import { Agent } from '../types';

interface AgentCardProps {
  agent: Agent;
  onPause: (id: string) => void;
  onResume: (id: string) => void;
  onTerminate: (id: string) => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  onPause,
  onResume,
  onTerminate,
}) => {
  const getStateColor = (state: string) => {
    const colors: Record<string, string> = {
      idle: 'bg-green-100',
      working: 'bg-blue-100',
      paused: 'bg-yellow-100',
      error: 'bg-red-100',
      terminated: 'bg-gray-100',
    };
    return colors[state] || 'bg-gray-100';
  };

  return (
    <div className={`p-4 rounded-lg ${getStateColor(agent.state)}`}>
      <h3 className="font-bold">{agent.name}</h3>
      <p className="text-sm">State: {agent.state}</p>
      <p className="text-sm">Capabilities: {agent.capabilities.join(', ')}</p>
      <div className="mt-2 flex gap-2">
        {agent.state === 'idle' && (
          <button onClick={() => onPause(agent.id)} className="btn">
            Pause
          </button>
        )}
        {agent.state === 'paused' && (
          <button onClick={() => onResume(agent.id)} className="btn">
            Resume
          </button>
        )}
        <button onClick={() => onTerminate(agent.id)} className="btn btn-danger">
          Terminate
        </button>
      </div>
    </div>
  );
};
```

**File**: `dashboard/src/components/EventLog.tsx`
```typescript
interface EventLogProps {
  events: any[];
  onClear: () => void;
}

export const EventLog: React.FC<EventLogProps> = ({ events, onClear }) => {
  return (
    <div className="border rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Event Log</h2>
        <button onClick={onClear} className="btn btn-small">
          Clear
        </button>
      </div>
      <div className="h-64 overflow-y-auto">
        {events.map((event, idx) => (
          <div key={idx} className="border-b p-2">
            <p className="text-sm font-mono text-gray-600">
              {new Date(event.timestamp).toLocaleTimeString()}
            </p>
            <p className="text-sm">{event.event_type}</p>
            <p className="text-xs text-gray-500">{event.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
```

**File**: `dashboard/src/components/MetricsDashboard.tsx`
```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface MetricsDashboardProps {
  metrics: any[];
  agentId: string;
}

export const MetricsDashboard: React.FC<MetricsDashboardProps> = ({ metrics, agentId }) => {
  return (
    <div className="border rounded-lg p-4">
      <h2 className="text-xl font-bold mb-4">Agent {agentId} Metrics</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={metrics}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="cpu_percent" stroke="#8884d8" name="CPU %" />
          <Line type="monotone" dataKey="memory_mb" stroke="#82ca9d" name="Memory (MB)" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
```

### Dashboard Pages (T078-T080)

**File**: `dashboard/src/pages/Overview.tsx`
- Grid of active agents with status indicators
- Summary metrics (total agents, tasks in queue, etc.)
- Recent events sidebar

**File**: `dashboard/src/pages/Agents.tsx`
- Full list of agents with filtering
- Detailed agent view with metrics
- Spawn new agent form

**File**: `dashboard/src/pages/Monitoring.tsx`
- Real-time event stream
- Performance metrics charts
- Resource utilization graphs

### Real-Time Updates (T081-T083)
- Connect WebSocket in useEffect
- Update dashboard state on events
- Display toast notifications for critical events

**Validation**:
- Dashboard renders without errors
- Can see agent list from backend
- Real-time updates work via WebSocket
- Metrics display correctly

**Checkpoint**: US2 Dashboard fully functional ✓

---

## Phase 6: US4 - Visualize and Edit Workflows (T111-T123)

**Status**: BLOCKED until US3 (Workflows API) complete

### Workflow Editor Component (T111-T114)

**File**: `dashboard/src/components/WorkflowEditor.tsx`
```typescript
import ReactFlow, { 
  Node, 
  Edge, 
  useNodesState, 
  useEdgesState, 
  addEdge,
  Connection,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface WorkflowEditorProps {
  onSave: (nodes: Node[], edges: Edge[]) => void;
  initialNodes?: Node[];
  initialEdges?: Edge[];
}

export const WorkflowEditor: React.FC<WorkflowEditorProps> = ({
  onSave,
  initialNodes = [],
  initialEdges = [],
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = (connection: Connection) => {
    setEdges((eds) => addEdge(connection, eds));
  };

  return (
    <div className="w-full h-screen">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
      >
        <button
          onClick={() => onSave(nodes, edges)}
          className="absolute top-4 right-4 btn btn-primary"
        >
          Save Workflow
        </button>
      </ReactFlow>
    </div>
  );
};
```

**File**: `dashboard/src/pages/Workflows.tsx`
- List of workflows with start/stop actions
- Integrate WorkflowEditor component
- Real-time execution progress overlay

**Validation**:
- Can create workflow visually
- Can connect nodes with edges
- Save creates workflow in backend
- Load workflow renders correctly

**Checkpoint**: US4 Visualization complete ✓

---

## Success Criteria

- [ ] Dashboard starts without errors
- [ ] Can list agents from backend API
- [ ] Real-time WebSocket updates working
- [ ] Metrics display correctly in charts
- [ ] Can pause/resume/terminate agents
- [ ] Event log shows live updates
- [ ] Workflow editor functional
- [ ] All pages responsive and styled

## Communication Protocol

After completing Phase 4 (US2):

```json
{
  "agent": "frontend-developer",
  "phase": "phase_4_us2_complete",
  "timestamp": "2025-11-04T...",
  "tasks_completed": ["T011", "T012", "T056", "T057", ..., "T083"],
  "checkpoint_validated": true,
  "next_phase": "phase_6_us4"
}
```

Commit:
```bash
git add dashboard/
git commit -m "feat(frontend): implement dashboard (T071-T083)

- Create React SPA with Vite
- Implement API client and WebSocket service
- Build dashboard components (agents, events, metrics)
- Create pages for overview, agents, monitoring
- Integrate real-time updates

US2 Dashboard complete and functional.

Co-authored-by: factory-droid[bot] <138933559+factory-droid[bot]@users.noreply.github.com>"
```

## Reference Documents
- API Spec: `specs/001-multi-agent-framework/contracts/api-spec.yaml`
- Quickstart: `specs/001-multi-agent-framework/quickstart.md`
- Architecture: `specs/001-multi-agent-framework/plan.md`

**Priority**: P2 - Start Phase 1 now, Phase 4+ after backend Phase 2 complete
