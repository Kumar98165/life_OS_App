# LifeOS AI Automation Security & Safety Architecture

> **Version**: 1.0.0  
> **Date**: 2026-11-08  
> **Status**: Verified

---

## 1. Threat Model & Mitigations

### 1.1 Prompt Injection & Unauthorized Tool Invocations
- **Threat**: Adversary embeds instructions into a task title or note to coerce the LLM into invoking dangerous tools.
- **Mitigation**: The LLM has zero direct execution power. Actions are output as structured JSON objects that pass through `node_validate_actions`. Any tool not explicitly found in `automation_tool_registry` is rejected with an audit log.

### 1.2 Arbitrary Code Execution
- **Threat**: Model proposes raw Python, Bash, or SQL snippets.
- **Mitigation**: No `eval()`, `exec()`, or raw SQL execution endpoints exist. Only pre-compiled Python service methods in the tool registry can run.

### 1.3 In-Flight Action Tampering
- **Threat**: Action parameters are altered between proposing the action and user approval.
- **Mitigation**: When an approval record is created, a SHA-256 hash of the canonical JSON parameters is stored (`parameter_hash`). When `/approve` is called, the parameter hash is recalculated and verified against the stored hash. Any mutation results in instant abort.

### 1.4 Financial Integrity
- **Threat**: AI executes payments, drains balances, or alters transaction history.
- **Mitigation**: The finance automation tool (`finance.get_financial_summary`) is strictly read-only. No write or transfer tools are registered.

### 1.5 Approval Expiry
- **Threat**: Stale action proposals executed days later when user context has shifted.
- **Mitigation**: Approvals possess an explicit 24-hour expiration window (`expires_at`). The service validates timestamp freshness on approval attempts and marks expired requests accordingly.

### 1.6 Duplicate Execution Protection
- **Threat**: Network retries or rapid user taps cause multiple identical actions.
- **Mitigation**: `AutomationExecution` records enforce optional `idempotency_key` tokens. Scheduled background jobs generate deterministic date-stamped keys (`scheduled:{slug}:{uid}:{date}`) to prevent double-firing.
