# Tasks: Extended Analysis Agents (v3.0.1)

**Branch**: `008-extended-agents`
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)
**Total Tasks**: 42

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
- [ ] T010 [P] Add `TechnicalDebtItem` dataclass to `src/models/data_models.py`
- [ ] T011 [P] Add `DocumentationGap` dataclass to `src/models/data_models.py`
- [ ] T012 [P] Add `TypeSafetyIssue` dataclass to `src/models/data_models.py`
- [ ] T013 [P] Add `PrivacyViolation` dataclass to `src/models/data_models.py`

---

## Phase 3: Workflow Integration

**Goal**: Add new workflow stages for extended agents

### Independent Test
Verify new WorkflowStage enum values are recognized by orchestrator.

- [ ] T014 Add 6 new WorkflowStage enum values to `src/core/orchestrator.py`
- [ ] T015 Register new workflow stages in orchestration flow `src/core/orchestrator.py`
- [ ] T016 Add report generation paths for new agents in `src/core/analyzer.py`

---

## Phase 4: User Story 2 - Documentation Agent (P2)

**Goal**: Detect missing docstrings, stale comments, undocumented parameters

### Independent Test
Analyze a file without docstrings and verify missing_docstring issues are reported.

- [ ] T017 [US2] Create `src/agents/documentation_agent.py` with BaseAgent inheritance
- [ ] T018 [US2] Implement docstring detection patterns (Python, TypeScript, Java)
- [ ] T019 [US2] Implement stale comment detection (comment vs code mismatch)
- [ ] T020 [US2] Implement undocumented parameter detection
- [ ] T021 [US2] Add documentation_report.md generation in `src/core/analyzer.py`
- [ ] T022 [US2] Add unit tests in `tests/unit/agents/test_documentation_agent.py`

---

## Phase 5: User Story 6 - Type Safety Agent (P2)

**Goal**: Detect any usage, unsafe casts, null safety violations

### Independent Test
Analyze a TypeScript file with `any` and verify any_usage issues are reported.

- [ ] T023 [US6] Create `src/agents/type_safety_agent.py` with BaseAgent inheritance
- [ ] T024 [US6] Implement `any`/`Any` detection patterns
- [ ] T025 [US6] Implement unsafe cast detection (`as any`, `# type: ignore`)
- [ ] T026 [US6] Implement null safety check patterns
- [ ] T027 [US6] Add type_safety_report.md generation in `src/core/analyzer.py`
- [ ] T028 [US6] Add unit tests in `tests/unit/agents/test_type_safety_agent.py`

---

## Phase 6: User Story 4 - Technical Debt Agent (P2)

**Goal**: Detect code smells, TODO/FIXME, circular dependencies

### Independent Test
Analyze a file with TODO comments and verify they are collected.

- [ ] T029 [US4] Create `src/agents/technical_debt_agent.py` with BaseAgent inheritance
- [ ] T030 [US4] Implement code smell detection (God class, long method)
- [ ] T031 [US4] Implement TODO/FIXME/HACK collection
- [ ] T032 [US4] Implement circular dependency detection
- [ ] T033 [US4] Add technical_debt_report.md generation in `src/core/analyzer.py`
- [ ] T034 [US4] Add unit tests in `tests/unit/agents/test_technical_debt_agent.py`

---

## Phase 7: User Story 2 - Performance Agent (P1)

**Goal**: Detect O(n²) patterns, N+1 queries, memory leaks

### Independent Test
Analyze a file with nested loops on same collection and verify complexity issue reported.

- [ ] T035 [US2] Create `src/agents/performance_analysis_agent.py` with BaseAgent inheritance
- [ ] T036 [US2] Implement O(n²)/O(n³) detection (nested loops)
- [ ] T037 [US2] Implement N+1 query pattern detection
- [ ] T038 [US2] Implement memory leak pattern detection (unclosed resources)
- [ ] T039 [US2] Implement blocking async detection
- [ ] T040 [US2] Add performance_report.md generation in `src/core/analyzer.py`
- [ ] T041 [US2] Add unit tests in `tests/unit/agents/test_performance_agent.py`

---

## Phase 8: User Story 3 - API Contract Agent (P1)

**Goal**: Detect REST violations, breaking changes, undocumented endpoints

### Independent Test
Analyze an API with GET body and verify HTTP method violation reported.

- [ ] T042 [US3] Create `src/agents/api_contract_agent.py` with BaseAgent inheritance
- [ ] T043 [US3] Implement HTTP method violation detection
- [ ] T044 [US3] Implement REST naming consistency checks
- [ ] T045 [US3] Implement breaking change detection
- [ ] T046 [US3] Implement undocumented endpoint detection
- [ ] T047 [US3] Add api_contract_report.md generation in `src/core/analyzer.py`
- [ ] T048 [US3] Add unit tests in `tests/unit/agents/test_api_contract_agent.py`

---

## Phase 9: User Story 7 - Data Privacy Agent (P3)

**Goal**: Detect PII logging, missing encryption, compliance violations

### Independent Test
Configure `compliance_agents: ["gdpr"]` and verify PII in logs is detected.

- [ ] T049 [US7] Create `src/agents/data_privacy_agent.py` with BaseAgent inheritance
- [ ] T050 [US7] Implement PII detection patterns (email, SSN, phone)
- [ ] T051 [US7] Implement sensitive data encryption checks
- [ ] T052 [US7] Implement compliance framework mapping (GDPR, HIPAA, PCI_DSS, CCPA)
- [ ] T053 [US7] Add privacy_report.md generation in `src/core/analyzer.py`
- [ ] T054 [US7] Add unit tests in `tests/unit/agents/test_data_privacy_agent.py`

---

## Phase 10: Polish & Integration

**Goal**: Final integration, documentation, edge case handling

- [ ] T055 [P] Update README.md agent table (6 → 12 agents)
- [ ] T056 [P] Update docs/agents.md with new agent descriptions
- [ ] T057 [P] Update docs/configuration.md with new config options
- [ ] T058 Add integration test for all 12 agents in `tests/integration/test_extended_agents.py`
- [ ] T059 Implement graceful degradation for agent failures in `src/core/analyzer.py`
- [ ] T060 Add invalid agent name validation with helpful error messages
- [ ] T061 Verify parallel execution performance (+50% max degradation)
- [ ] T062 Final lint and typecheck pass

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
     ├──► Phase 4 (Documentation Agent) ─────────────┐
     ├──► Phase 5 (Type Safety Agent) ───────────────┤
     ├──► Phase 6 (Technical Debt Agent) ────────────┼──► Phase 10 (Polish)
     ├──► Phase 7 (Performance Agent) ───────────────┤
     ├──► Phase 8 (API Contract Agent) ──────────────┤
     └──► Phase 9 (Data Privacy Agent) ──────────────┘
```

## Parallel Execution Examples

### Phase 2 - All dataclass tasks [P] can run in parallel
```
T008, T009, T010, T011, T012, T013 → parallel
```

### Phase 4-9 - Agent implementation phases can run in parallel
```
Phase 4 || Phase 5 || Phase 6 || Phase 7 || Phase 8 || Phase 9
```

### Phase 10 - Documentation updates [P] can run in parallel
```
T055, T056, T057 → parallel
```

---

## Implementation Strategy

1. **MVP**: Phase 1-3 + Documentation Agent (Phase 4)
2. **Iteration 1**: Add Type Safety + Technical Debt agents
3. **Iteration 2**: Add Performance + API Contract agents
4. **Iteration 3**: Add Data Privacy agent + Polish

---

## Acceptance Criteria Summary

| User Story | Tasks | Independent Test |
|------------|-------|------------------|
| US1: Agent Activation | T001-T007 | `--agents` filters correctly |
| US2: Performance | T035-T041 | O(n²) detected |
| US3: API Contract | T042-T048 | GET body violation detected |
| US4: Technical Debt | T029-T034 | TODO collected |
| US5: Documentation | T017-T022 | Missing docstring detected |
| US6: Type Safety | T023-T028 | any usage detected |
| US7: Compliance | T049-T054 | PII in logs detected |
