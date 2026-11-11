# Feature Specification: README Restructure

**Feature Branch**: `013-readme-restructure`
**Created**: 2026-01-08
**Status**: Draft
**Input**: User description: "Restructure README.md with two clear sections: 1) Top marketing section containing the poll, download stats badges, value proposition, and social proof to sell WHY the package is essential. 2) Technical section with architecture diagram (mermaid) showing how the 6-agent system works, the analysis flow, and integration points."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First-Time Visitor Evaluates Package (Priority: P1)

A developer discovers Aetheris (via PyPI, GitHub search, or referral) and needs to quickly determine if the package solves their code review pain points. They scan the top of the README to understand the value proposition and see social proof (downloads, poll engagement) before deciding to continue reading.

**Why this priority**: First impressions determine conversion. If the top section fails to communicate value, users leave before reaching technical details.

**Independent Test**: Can be validated by user feedback on comprehension of value proposition within 30 seconds of reading.

**Acceptance Scenarios**:

1. **Given** a developer lands on the README, **When** they spend 30 seconds scanning the top section, **Then** they understand what Aetheris does and why they should care
2. **Given** a developer sees the download stats and poll, **When** they evaluate credibility, **Then** they perceive the project as actively maintained and community-driven
3. **Given** a developer is evaluating code review tools, **When** they read the value proposition, **Then** they can identify at least 3 pain points Aetheris solves

---

### User Story 2 - Technical Lead Evaluates Architecture (Priority: P2)

A technical lead or architect considering Aetheris for their team needs to understand how the 6-agent system works, the data flow, and integration points before recommending adoption.

**Why this priority**: After marketing hooks interest, technical buyers need architectural clarity to make adoption decisions.

**Independent Test**: Can be tested by showing the technical section to an architect unfamiliar with the project and measuring if they can explain the system in their own words.

**Acceptance Scenarios**:

1. **Given** a technical lead reads the architecture section, **When** they view the diagram, **Then** they understand the analysis flow from CLI to final report
2. **Given** an architect evaluates the 6-agent system, **When** they read the agent descriptions, **Then** they understand each agent's responsibility and how they coordinate
3. **Given** a DevOps engineer checks integration points, **When** they review the technical section, **Then** they identify how Aetheris integrates with CI/CD pipelines

---

### User Story 3 - Contributor Understands System Design (Priority: P3)

A potential contributor wants to understand the internal architecture before submitting a PR or extending the agent system.

**Why this priority**: Contributors need technical context, but they are a smaller audience than users.

**Independent Test**: Can be validated by asking a new contributor to locate where to add a new agent based on the README diagram.

**Acceptance Scenarios**:

1. **Given** a contributor reads the README, **When** they view the architecture diagram, **Then** they understand the component hierarchy (CLI → Orchestrator → Agents)
2. **Given** a developer wants to add a new agent, **When** they read the technical section, **Then** they understand the agent integration pattern

---

### Edge Cases

- What happens when PyPI badges fail to load? (Alt text provides fallback information)
- How does the mermaid diagram render on non-GitHub platforms? (Include text description as fallback)
- What if the poll service is down? (Link remains functional even if SVG badges fail)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: README MUST have a clearly delineated marketing section at the top (before any technical content)
- **FR-002**: Marketing section MUST include download statistics badges (PyPI total, monthly, weekly)
- **FR-003**: Marketing section MUST include the community poll about open-sourcing with live voting buttons
- **FR-004**: Marketing section MUST communicate 3+ key value propositions with clear pain-point → solution mapping
- **FR-005**: Marketing section MUST include social proof elements (download stats, comparison table vs alternatives)
- **FR-006**: README MUST have a technical section with a mermaid architecture diagram
- **FR-007**: Architecture diagram MUST show the 6 specialized agents and their responsibilities
- **FR-008**: Architecture diagram MUST illustrate the analysis flow (CLI → Orchestrator → Agents → Report)
- **FR-009**: Technical section MUST explain integration points (AI providers, CI/CD, GitHub)
- **FR-010**: README MUST maintain mobile-friendly formatting (no overly wide tables or code blocks)
- **FR-011**: Poll section MUST be prominent in the marketing section (top 30% of README)
- **FR-012**: README structure MUST guide readers from "why" (marketing) to "how" (technical) to "get started" (quickstart)

### Key Entities

- **Marketing Section**: Title, tagline, badges, value proposition table, poll embed, social proof
- **Technical Section**: Architecture diagram, agent descriptions, integration points, data flow explanation
- **Quick Start Section**: Installation, configuration, first command (kept concise)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: First-time visitors understand Aetheris value proposition within 30 seconds of landing on README
- **SC-002**: The poll is visible in the top marketing section before technical content
- **SC-003**: Technical leads can explain the 6-agent architecture after reading the technical section
- **SC-004**: README renders correctly on GitHub, PyPI, and markdown viewers with no broken elements
- **SC-005**: Architecture diagram conveys data flow in a single glance (3-5 seconds to grasp high-level flow)
- **SC-006**: README maintains current keywords for discoverability (AI code review, security analysis, architecture review)

## Assumptions

- The existing poll service at adryanserage.ca remains operational
- Mermaid diagrams are natively supported by GitHub (confirmed)
- PyPI badges from shields.io and pepy.tech remain stable
- Current README content is accurate and only needs restructuring, not rewriting
- Mobile users represent a minority of README readers (developer documentation typically accessed on desktop)
