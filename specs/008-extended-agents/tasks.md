# Tasks: Extended Analysis Agents (v3.0.1)

**Branch**: `008-extended-agents`
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)
**Total Tasks**: 44

---

## Phase 1: Setup & Configuration

**Goal**: Extend configuration system to support agent activation and compliance settings

### Independent Test
Run `aetheris analysis --agents performance` and verify only performance agent (+ core 6) executes.

- [ ] T001 Add `enabled_agents` and `compliance_agents` fields to AnalysisConfig in `src/core/config.py`
- [ ] T002 Add config.json schema validation for new agent fields in `src/core/config.py`
- [ ] T003 [P] Add `--agents` CLI option to `src/cli.py`
- [ ] T004 [P] Add `--skip-agents` CLI option to `src/cli.py`
- [ ] T005 [P] Add `--compliance` CLI option to `src/cli.py`
- [ ] T006 Implement agent filtering logic in `src/core/analyzer.py`
- [ ] T007 Add unit tests for configuration parsing in `tests/unit/test_config.py`

---

## Phase 2: Data Models

**Goal**: Define dataclasses for all new agent outputs

### Independent Test
Import all new dataclasses and verify Pydantic serialization works.

- [ ] T008 [P] Add `PerformanceIssue` dataclass to `src/models/data_models.py`
- [ ] T009 [P] Add `APIContractViolation` dataclass to `src/models/data_models.py`
- [ ] T010 [P] Add `TypeSafetyIssue` dataclass to `src/models/data_models.py`
- [ ] T011 [P] Add `PrivacyViolation` dataclass to `src/models/data_models.py`

---

## Phase 3: Workflow Integration

**Goal**: Add new workflow stages for extended agents

### Independent Test
Verify new WorkflowStage enum values are recognized by orchestrator.

- [ ] T012 Add 4 new WorkflowStage enum values to `src/core/orchestrator.py`
- [ ] T013 Register new workflow stages in orchestration flow `src/core/orchestrator.py`
- [ ] T014 Add report generation paths for new agents in `src/core/analyzer.py`

---

## Phase 4: User Story 4 - Type Safety Agent (P2)

**Goal**: Detect any usage, unsafe casts, null safety violations

### Independent Test
Analyze a TypeScript file with `any` and verify any_usage issues are reported.

- [ ] T015 [US4] Create `src/agents/type_safety_agent.py` with BaseAgent inheritance
- [ ] T016 [US4] Implement `any`/`Any` detection patterns
- [ ] T017 [US4] Implement unsafe cast detection (`as any`, `# type: ignore`)
- [ ] T018 [US4] Implement null safety check patterns
- [ ] T019 [US4] Add type_safety_report.md generation in `src/core/analyzer.py`
- [ ] T020 [US4] Add unit tests in `tests/unit/agents/test_type_safety_agent.py`

---

## Phase 5: User Story 2 - Performance Agent (P1)

**Goal**: Detect O(n²) patterns, N+1 queries, memory leaks

### Independent Test
Analyze a file with nested loops on same collection and verify complexity issue reported.

- [ ] T021 [US2] Create `src/agents/performance_analysis_agent.py` with BaseAgent inheritance
- [ ] T022 [US2] Implement O(n²)/O(n³) detection (nested loops)
- [ ] T023 [US2] Implement N+1 query pattern detection
- [ ] T024 [US2] Implement memory leak pattern detection (unclosed resources)
- [ ] T025 [US2] Implement blocking async detection
- [ ] T026 [US2] Add performance_report.md generation in `src/core/analyzer.py`
- [ ] T027 [US2] Add unit tests in `tests/unit/agents/test_performance_agent.py`

---

## Phase 6: User Story 3 - API Contract Agent (P1)

**Goal**: Detect REST violations, breaking changes, undocumented endpoints

### Independent Test
Analyze an API with GET body and verify HTTP method violation reported.

- [ ] T028 [US3] Create `src/agents/api_contract_agent.py` with BaseAgent inheritance
- [ ] T029 [US3] Implement HTTP method violation detection
- [ ] T030 [US3] Implement REST naming consistency checks
- [ ] T031 [US3] Implement breaking change detection
- [ ] T032 [US3] Implement undocumented endpoint detection
- [ ] T033 [US3] Add api_contract_report.md generation in `src/core/analyzer.py`
- [ ] T034 [US3] Add unit tests in `tests/unit/agents/test_api_contract_agent.py`

---

## Phase 7: User Story 5 - Data Privacy Agent (P3)

**Goal**: Detect PII logging, missing encryption, compliance violations

### Independent Test
Configure `compliance_agents: ["gdpr"]` and verify PII in logs is detected.

- [ ] T035 [US5] Create `src/agents/data_privacy_agent.py` with BaseAgent inheritance
- [ ] T036 [US5] Implement PII detection patterns (email, SSN, phone)
- [ ] T037 [US5] Implement sensitive data encryption checks
- [ ] T038 [US5] Implement compliance framework mapping (GDPR, HIPAA, PCI_DSS, CCPA)
- [ ] T039 [US5] Add privacy_report.md generation in `src/core/analyzer.py`
- [ ] T040 [US5] Add unit tests in `tests/unit/agents/test_data_privacy_agent.py`

---

## Phase 8: Polish & Integration

**Goal**: Final integration, documentation, edge case handling

- [ ] T041 [P] Update README.md agent table (6 → 10 agents)
- [ ] T042 [P] Update docs/agents.md with new agent descriptions
- [ ] T043 [P] Update docs/configuration.md with new config options
- [ ] T044 Add integration test for all 10 agents in `tests/integration/test_extended_agents.py`
- [ ] T045 Implement graceful degradation for agent failures in `src/core/analyzer.py`
- [ ] T046 Add invalid agent name validation with helpful error messages
- [ ] T047 Verify parallel execution performance (+30% max degradation)
- [ ] T048 Final lint and typecheck pass

---

## Dependencies

```
Phase 1 (Setup) ─────────────────────────────────────┐
                                                      │
Phase 2 (Data Models) ───────────────────────────────┼──► Phase 3 (Workflow)
                                                      │
Phase 3 (Workflow) ──────────────────────────────────┤
                                                      │
     ┌────────────────────────────────────────────────┘
     │
     ├──► Phase 4 (Type Safety Agent) ───────────────┐
     ├──► Phase 5 (Performance Agent) ───────────────┼──► Phase 8 (Polish)
     ├──► Phase 6 (API Contract Agent) ──────────────┤
     └──► Phase 7 (Data Privacy Agent) ──────────────┘
```

## Parallel Execution Examples

### Phase 2 - All dataclass tasks [P] can run in parallel
```
T008, T009, T010, T011 → parallel
```

### Phase 4-7 - Agent implementation phases can run in parallel
```
Phase 4 || Phase 5 || Phase 6 || Phase 7
```

### Phase 8 - Documentation updates [P] can run in parallel
```
T041, T042, T043 → parallel
```

---

## Implementation Strategy

1. **MVP**: Phase 1-3 + Type Safety Agent (Phase 4)
2. **Iteration 1**: Add Performance Agent
3. **Iteration 2**: Add API Contract Agent
4. **Iteration 3**: Add Data Privacy Agent + Polish

---

## Acceptance Criteria Summary

| User Story | Tasks | Independent Test |
|------------|-------|------------------|
| US1: Agent Activation | T001-T007 | `--agents` filters correctly |
| US2: Performance | T021-T027 | O(n²) detected |
| US3: API Contract | T028-T034 | GET body violation detected |
| US4: Type Safety | T015-T020 | any usage detected |
| US5: Compliance | T035-T040 | PII in logs detected |

---

## ROI Summary

**4 agents instead of 6** = Better value for users:

| Kept | Why |
|------|-----|
| Performance | Prevents costly production perf bugs |
| API Contract | 80% bugs at integration points |
| Type Safety | Type discipline prevents runtime errors |
| Data Privacy | Compliance fines are expensive |

| Removed | Why |
|---------|-----|
| ~~Technical Debt~~ | Overlaps with Code Metrics + Architect |
| ~~Documentation~~ | ESLint/Pylint plugins do this better |
