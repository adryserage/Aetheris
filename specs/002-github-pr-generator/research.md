# Research: GitHub PR Generator

**Feature**: 002-github-pr-generator
**Date**: 2026-01-06

## Decision 1: Bug Parsing Approach

**Decision**: Reuse `IssueCreator` class from `issue_creator.py`

**Rationale**:
- Already implemented and tested bug extraction from analysis reports
- Same data model (`ExtractedBug`) can be used
- DRY principle - avoid code duplication

**Alternatives Considered**:
- Create new parser: Rejected - unnecessary duplication
- Copy code: Rejected - maintenance burden

## Decision 2: AI Fix Generation

**Decision**: Use existing `AIProvider` abstraction with specialized fix prompt

**Rationale**:
- Leverages existing Gemini/OpenAI/Claude integration
- Consistent with project architecture
- No new dependencies

**Implementation**:
```python
prompt = f"""
Fix the following bug in {file_path}:

Bug: {bug.description}
Severity: {bug.severity}
Type: {bug.bug_type}

Current code context:
```{language}
{code_context}
```

Provide ONLY the fixed code, no explanations.
"""
```

## Decision 3: Git Branch Strategy

**Decision**: Create ephemeral branches per bug, push immediately

**Rationale**:
- Each bug gets isolated fix
- Easy to review individually
- Can be merged independently

**Branch Format**: `fix/<bug-type>-<filename>-<hash>`
- `bug-type`: security, risk, inconsistency, suggestion
- `filename`: basename without extension
- `hash`: first 6 chars of bug title hash

## Decision 4: Syntax Validation

**Decision**: Use `py_compile` for Python, `node --check` for JS/TS

**Rationale**:
- Quick validation before commit
- Prevents obviously broken code from being PR'd
- Uses standard tooling

**Fallback**: If validation fails, create placeholder PR with TODO marker.

## Decision 5: Issue Linking

**Decision**: Match by normalized title comparison

**Rationale**:
- Issues created by `aetheris issues` have predictable title format
- `[Type] in filename - description` pattern is searchable
- Use `gh issue list --json title,number` to fetch existing issues

**Matching Algorithm**:
1. Format expected issue title from bug
2. Search existing issues
3. Match by case-insensitive title prefix
4. Use first match as `Fixes #N` target

## Decision 6: Rate Limiting

**Decision**: Reuse exponential backoff pattern from issue_creator

**Rationale**:
- Proven pattern already in codebase
- Handles both GitHub API and AI provider limits
- Consistent user experience
