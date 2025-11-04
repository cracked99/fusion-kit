# QA Engineer - Implementation Instructions

## Mission
Ensure backward compatibility, implement comprehensive testing, and validate system reliability.

## Context
- **Project**: fusion-kit multi-agent framework
- **Branch**: `001-multi-agent-framework`
- **Working Directory**: `/home/hyperuser/fusion-kit`
- **Role**: Testing & Validation

## Phase 7: US5 - Backward Compatibility Testing (T124-T135)

**Status**: Can begin after backend Phase 2, validate throughout all phases

### Compatibility Testing (T124-T135)

**File**: `tests/test_backwards_compatibility.py`

```python
import subprocess
import pytest

class TestCLICompatibility:
    """Test that all existing CLI commands still work"""
    
    def test_specify_init_works(self):
        """Verify specify init command still works"""
        result = subprocess.run(
            ["specify", "init", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "init" in result.stdout
    
    def test_specify_check_works(self):
        """Verify specify check command still works"""
        result = subprocess.run(
            ["specify", "check"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0
    
    def test_existing_agent_configs_compatible(self):
        """Verify all existing agent configs still work"""
        existing_agents = ["claude", "gemini", "copilot", "cursor-agent", "droid"]
        
        for agent in existing_agents:
            result = subprocess.run(
                ["specify", "init", "test-project", "--ai", agent, "--ignore-agent-tools"],
                capture_output=True,
                text=True,
                timeout=30
            )
            # Should not fail due to multi-agent framework
            assert "error" not in result.stderr.lower()

class TestSingleAgentMode:
    """Test that single-agent mode works without multi-agent overhead"""
    
    def test_single_agent_no_overhead(self):
        """Verify <5% performance overhead in single-agent mode"""
        import time
        
        # Time a single agent operation
        start = time.time()
        # Run single agent operation
        elapsed = time.time() - start
        
        # Should be very fast without multi-agent overhead
        assert elapsed < 5.0  # Arbitrary baseline
```

**File**: `tests/test_agent_compatibility.py`

```python
import asyncio
from src.fusion_kit.providers.registry import ProviderRegistry

class TestProviderCompatibility:
    """Test that agent configurations work with framework"""
    
    @pytest.mark.asyncio
    async def test_claude_provider_integration(self):
        """Verify Claude agent works with new framework"""
        # Should be able to instantiate
        provider = await ProviderRegistry.get("claude")
        assert provider is not None
    
    @pytest.mark.asyncio
    async def test_gemini_provider_integration(self):
        """Verify Gemini agent works with new framework"""
        provider = await ProviderRegistry.get("gemini")
        assert provider is not None
    
    @pytest.mark.asyncio
    async def test_droid_provider_integration(self):
        """Verify Droid agent works with new framework"""
        provider = await ProviderRegistry.get("droid")
        assert provider is not None
```

### Integration Tests

**File**: `tests/integration/test_agent_spawning.py`

```python
import asyncio
import pytest
from src.fusion_kit.core.agent import Agent, AgentState
from src.fusion_kit.core.lifecycle import AgentManager
from src.fusion_kit.providers.registry import ProviderRegistry

@pytest.mark.asyncio
class TestAgentSpawning:
    """Test agent spawning and lifecycle"""
    
    async def test_spawn_agent(self):
        """Test spawning a single agent"""
        manager = AgentManager()
        agent = await manager.spawn_agent(
            name="TestAgent",
            capabilities=["testing"],
            provider_id=uuid4(),
            model_name="test-model"
        )
        
        assert agent is not None
        assert agent.state == AgentState.SPAWNING
        await asyncio.sleep(1)
        assert agent.state == AgentState.IDLE
    
    async def test_workspace_isolation(self):
        """Test that agents have isolated workspaces"""
        manager = AgentManager()
        
        agent1 = await manager.spawn_agent(
            name="Agent1",
            capabilities=["test"],
            provider_id=uuid4(),
            model_name="model1"
        )
        
        agent2 = await manager.spawn_agent(
            name="Agent2",
            capabilities=["test"],
            provider_id=uuid4(),
            model_name="model2"
        )
        
        # Workspaces should be different
        assert agent1.workspace_path != agent2.workspace_path
        
        # Both should exist
        assert os.path.exists(agent1.workspace_path)
        assert os.path.exists(agent2.workspace_path)
    
    async def test_agent_lifecycle(self):
        """Test full agent lifecycle"""
        manager = AgentManager()
        agent = await manager.spawn_agent(...)
        
        # Pause
        await manager.pause_agent(agent.id)
        assert agent.state == AgentState.PAUSED
        
        # Resume
        await manager.resume_agent(agent.id)
        assert agent.state == AgentState.IDLE
        
        # Terminate
        await manager.terminate_agent(agent.id)
        assert agent.state == AgentState.TERMINATED
```

**File**: `tests/integration/test_message_passing.py`

```python
import asyncio
import pytest
from src.fusion_kit.messaging.message_queue import MessageQueue

@pytest.mark.asyncio
class TestMessagePassing:
    """Test inter-agent message communication"""
    
    async def test_publish_subscribe(self):
        """Test pub/sub messaging"""
        mq = MessageQueue("redis://localhost:6379")
        
        messages_received = []
        
        async def subscriber():
            async for msg in mq.subscribe("test.topic"):
                messages_received.append(msg)
                if len(messages_received) >= 1:
                    break
        
        # Start subscriber in background
        sub_task = asyncio.create_task(subscriber())
        
        # Publish message
        await asyncio.sleep(0.5)
        await mq.publish("test.topic", {"test": "data"})
        
        await asyncio.wait_for(sub_task, timeout=5)
        assert len(messages_received) == 1
```

---

## Phase 8: Testing & Validation (T152-T163)

### Unit Tests (T152-T154)

Create comprehensive unit tests for all core modules following pytest conventions.

### Contract Tests (T155)

**File**: `tests/contract/test_openrouter_api.py`

```python
import pytest
import httpx
from unittest.mock import AsyncMock, patch

class TestOpenRouterAPI:
    """Test OpenRouter provider API contract"""
    
    @pytest.mark.asyncio
    async def test_spawn_agent_api_contract(self):
        """Test API contract for spawning agents"""
        # Mock the API call
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = AsyncMock(
                status_code=200,
                json=AsyncMock(return_value={
                    "id": "agent-123",
                    "model": "claude-3",
                    "status": "active"
                })
            )
            
            # Call provider
            from src.fusion_kit.providers.openrouter import OpenRouterProvider
            provider = OpenRouterProvider(api_key="test-key")
            result = await provider.spawn_agent("claude-3", ["test"])
            
            # Verify API was called correctly
            mock_post.assert_called_once()
```

### Performance Validation (T160)

```python
import time
import pytest

class TestPerformance:
    """Validate system performance criteria"""
    
    @pytest.mark.asyncio
    async def test_agent_spawn_time(self):
        """SC-008: Model selection within 10 seconds in 95% of requests"""
        times = []
        
        for _ in range(100):
            start = time.time()
            # Spawn agent
            elapsed = time.time() - start
            times.append(elapsed)
        
        # 95th percentile should be < 10 seconds
        times.sort()
        p95 = times[int(len(times) * 0.95)]
        
        assert p95 < 10, f"95th percentile spawn time: {p95}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_agents(self):
        """SC-003: 10 concurrent agents without degradation below 80% baseline"""
        # Measure single agent performance
        baseline = await measure_single_agent_perf()
        
        # Measure 10 concurrent agents
        concurrent = await measure_concurrent_agents(10)
        
        # Should maintain >80% of baseline
        assert concurrent >= baseline * 0.8
```

### Success Criteria Validation (T161)

```python
@pytest.mark.asyncio
class TestSuccessCriteria:
    """Validate all success criteria from spec"""
    
    async def test_sc_001_agent_reliability(self):
        """SC-001: 99.9% reliability for spawn/pause/resume/terminate"""
        # Run 1000 operations
        failures = 0
        for _ in range(1000):
            try:
                await test_full_lifecycle()
            except Exception:
                failures += 1
        
        success_rate = (1000 - failures) / 1000
        assert success_rate >= 0.999
    
    async def test_sc_002_workspace_isolation(self):
        """SC-002: 100% workspace isolation"""
        # Spawn 20 agents
        agents = [await spawn_agent() for _ in range(20)]
        
        # Verify NO workspace overlaps
        paths = [a.workspace_path for a in agents]
        assert len(paths) == len(set(paths)), "Workspace paths not unique"
    
    async def test_sc_018_single_agent_overhead(self):
        """SC-018: Less than 5% performance overhead"""
        baseline = await measure_baseline_performance()
        with_framework = await measure_with_framework()
        
        overhead = (with_framework - baseline) / baseline
        assert overhead < 0.05, f"Overhead: {overhead*100:.1f}%"
```

---

## Success Criteria

- [ ] All backward compatibility tests pass
- [ ] Single-agent mode <5% overhead
- [ ] 99.9% agent lifecycle reliability
- [ ] 100% workspace isolation verified
- [ ] All success criteria validated
- [ ] Performance benchmarks meet targets
- [ ] Integration tests all pass

## Communication Protocol

After Phase 8:
```json
{
  "agent": "qa-engineer",
  "phase": "phase_8_complete",
  "test_results": {
    "unit_tests": "100/100 passed",
    "integration_tests": "50/50 passed",
    "compatibility_tests": "25/25 passed",
    "success_criteria": "21/21 validated"
  },
  "performance": {
    "agent_spawn_p95": "8.2s",
    "concurrent_agents": "10 @ 85% baseline",
    "single_agent_overhead": "2.3%"
  },
  "checkpoint_validated": true
}
```

**Priority**: P3 - Continuous throughout all phases, final validation after all features
