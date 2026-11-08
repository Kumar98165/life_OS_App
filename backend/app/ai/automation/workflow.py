"""LifeOS - Advanced AI Automation LangGraph Workflow.

Orchestrates the 10-phase controlled execution lifecycle:
User Request
→ Intent Classification
→ Context Retrieval
→ Automation Planning
→ Action Validation
→ Risk Assessment
→ Approval Gate
→ Execution
→ Result Verification
→ Response Generation
"""
import json
import hashlib
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from langgraph.graph import StateGraph, START, END

from app.ai.config import get_llm
from app.ai.context_engine import LifeOSContextEngine
from app.ai.automation.tools import automation_tool_registry
from app.models.automation import (
    AutomationExecution,
    AutomationAction,
    AutomationApproval,
    AutomationExecutionLog,
    AutomationDefinition
)
from app.extensions import db


# -----------------------------------------------------------------------------
# LangGraph Workflow State
# -----------------------------------------------------------------------------

class AutomationWorkflowState(TypedDict):
    """Strongly typed state dictionary passed through LangGraph nodes."""
    execution_id: str
    user_id: str
    definition_slug: Optional[str]
    user_request: str
    trigger_payload: Dict[str, Any]

    # Node progression outputs
    intent: str
    context_data: Dict[str, Any]
    formatted_context: str
    raw_plan: str
    proposed_actions: List[Dict[str, Any]]
    validated_actions: List[Dict[str, Any]]
    risk_level: str
    requires_approval: bool
    approvals_created: List[Dict[str, Any]]
    executed_results: List[Dict[str, Any]]
    verification_passed: bool
    final_response: str
    error: Optional[str]
    status: str


# -----------------------------------------------------------------------------
# Helper Logging Function
# -----------------------------------------------------------------------------

def _log_step(execution_id: str, user_id: str, step_name: str, message: str, level: str = "info", details: Optional[Dict[str, Any]] = None):
    try:
        log_entry = AutomationExecutionLog(
            execution_id=execution_id,
            user_id=user_id,
            step_name=step_name,
            level=level,
            message=message,
            details=details or {}
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception:
        db.session.rollback()


# -----------------------------------------------------------------------------
# LangGraph Workflow Nodes
# -----------------------------------------------------------------------------

def node_classify_intent(state: AutomationWorkflowState) -> Dict[str, Any]:
    """Phase 1: Determine automation category and operational intent."""
    exec_id = state["execution_id"]
    user_id = state["user_id"]
    req = state.get("user_request", "").lower()
    slug = state.get("definition_slug")

    if slug:
        intent = slug
    elif any(k in req for k in ["day", "morning", "today schedule", "plan today"]):
        intent = "plan_my_day"
    elif any(k in req for k in ["week", "review", "weekly reflection"]):
        intent = "prepare_weekly_review"
    elif any(k in req for k in ["deadline", "due soon", "urgent"]):
        intent = "upcoming_deadline_assistant"
    elif any(k in req for k in ["habit", "streak", "missed", "recovery"]):
        intent = "habit_recovery_assistant"
    elif any(k in req for k in ["goal", "milestone"]):
        intent = "goal_progress_review"
    elif any(k in req for k in ["budget", "spending", "money", "finance"]):
        intent = "budget_awareness_assistant"
    else:
        intent = "daily_productivity_summary"

    _log_step(exec_id, user_id, "classification", f"Intent resolved to '{intent}'", details={"intent": intent})
    return {"intent": intent}


def node_retrieve_context(state: AutomationWorkflowState) -> Dict[str, Any]:
    """Phase 2: Assemble verified user domain context (Tasks, Habits, Goals, Schedule, Finance)."""
    exec_id = state["execution_id"]
    user_id = state["user_id"]

    engine = LifeOSContextEngine()
    context_data = engine.build_user_context(user_id)

    # Augment with verified read-only financial aggregates
    try:
        fin_summary = automation_tool_registry.execute_tool("finance.get_financial_summary", user_id, {})
        context_data["financial_summary"] = fin_summary
    except Exception as e:
        context_data["financial_summary"] = {"error": str(e)}

    formatted_context = engine.format_context_prompt(context_data)
    if "financial_summary" in context_data:
        fs = context_data["financial_summary"]
        formatted_context += f"\n--- Financial Aggregate (Month: {fs.get('month')}) ---\n"
        formatted_context += f"Income: ${fs.get('total_income', '0.00')}, Expenses: ${fs.get('total_expenses', '0.00')}, Net Savings: ${fs.get('net_savings', '0.00')}\n"

    _log_step(exec_id, user_id, "context_retrieval", "Domain context and ledger aggregates assembled successfully")
    return {
        "context_data": context_data,
        "formatted_context": formatted_context,
    }


def node_plan_automation(state: AutomationWorkflowState) -> Dict[str, Any]:
    """Phase 3: Invoke local Qwen LLM to formulate narrative response and structured action proposals."""
    exec_id = state["execution_id"]
    user_id = state["user_id"]
    intent = state.get("intent", "daily_productivity_summary")
    context_text = state.get("formatted_context", "")

    # Retrieve system instructions based on template intent
    from app.ai.automation.templates import AUTOMATION_TEMPLATES
    matched_template = next((t for t in AUTOMATION_TEMPLATES if t["slug"] == intent), None)
    template_instructions = (
        matched_template["system_instructions"]
        if matched_template
        else "You are an intelligent LifeOS personal automation assistant."
    )

    prompt = f"""{template_instructions}

CONTEXT DATA:
{context_text}

USER REQUEST:
{state.get("user_request", "Run automation")}

AVAILABLE TOOLS FOR PROPOSING ACTIONS:
1. tasks.create_task(title, description, priority, due_date, estimated_minutes)
2. planner.create_block(title, start_time, end_time, block_type, description)
3. notifications.create_reminder(title, reminder_time, description)

STRICT FORMATTING RULE:
Provide your response with two clearly demarcated sections:
SECTION 1: NARRATIVE
Provide a concise, helpful, structured analysis in markdown.

SECTION 2: PROPOSED_ACTIONS_JSON
A valid JSON array of action objects. If no operations are required, output: []
Each action object must strictly adhere to:
{{
  "tool_name": "tasks.create_task" | "planner.create_block" | "notifications.create_reminder",
  "action_type": "create_task" | "create_block" | "create_reminder",
  "description": "Short description of what this action does",
  "parameters": {{ ... parameters conforming to the tool ... }}
}}
Do NOT output code blocks or markdown around the JSON; simply place the raw JSON array under the SECTION 2 header.
"""

    llm = get_llm(temperature=0.3)
    try:
        response = llm.invoke(prompt)
        raw_text = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        _log_step(exec_id, user_id, "planning", f"LLM planning invocation failed: {str(e)}", level="error")
        # Fallback deterministic response
        raw_text = f"SECTION 1: NARRATIVE\nAutomation executed in deterministic fallback mode based on current records.\n\nSECTION 2: PROPOSED_ACTIONS_JSON\n[]"

    # Parse sections
    narrative = ""
    proposed_actions = []
    if "SECTION 2: PROPOSED_ACTIONS_JSON" in raw_text:
        parts = raw_text.split("SECTION 2: PROPOSED_ACTIONS_JSON")
        narrative = parts[0].replace("SECTION 1: NARRATIVE", "").strip()
        json_str = parts[1].strip()
        try:
            # Extract JSON array bounds if surrounded by text
            start_idx = json_str.find("[")
            end_idx = json_str.rfind("]")
            if start_idx != -1 and end_idx != -1:
                clean_json = json_str[start_idx:end_idx + 1]
                proposed_actions = json.loads(clean_json)
        except Exception as e:
            _log_step(exec_id, user_id, "planning", f"Failed to parse action JSON: {str(e)}", level="warning")
            proposed_actions = []
    else:
        narrative = raw_text.strip()
        proposed_actions = []

    _log_step(
        exec_id, user_id, "planning",
        f"Planning generated {len(proposed_actions)} proposed action(s)",
        details={"actions_count": len(proposed_actions)}
    )

    return {
        "raw_plan": raw_text,
        "final_response": narrative,
        "proposed_actions": proposed_actions,
    }


def node_validate_actions(state: AutomationWorkflowState) -> Dict[str, Any]:
    """Phase 4: Validate proposed actions against the permitted tool registry and schemas."""
    exec_id = state["execution_id"]
    user_id = state["user_id"]
    proposed = state.get("proposed_actions", [])
    validated_actions = []

    for idx, act in enumerate(proposed):
        tool_name = act.get("tool_name", "")
        tool_def = automation_tool_registry.get_tool(tool_name)

        if not tool_def:
            _log_step(exec_id, user_id, "action_validation", f"Disallowed tool '{tool_name}' rejected", level="warning")
            continue

        # Validate parameters with tool's Pydantic schema
        params = act.get("parameters", {})
        if tool_def.schema_cls:
            try:
                validated_model = tool_def.schema_cls(**params)
                params = validated_model.model_dump()
            except Exception as e:
                _log_step(exec_id, user_id, "action_validation", f"Parameters for '{tool_name}' failed validation: {str(e)}", level="warning")
                continue

        validated_actions.append({
            "sequence_order": idx + 1,
            "tool_name": tool_name,
            "action_type": act.get("action_type", tool_name.split(".")[-1]),
            "description": act.get("description", f"Execute {tool_name}"),
            "risk_level": tool_def.risk_level,
            "requires_approval": tool_def.requires_approval,
            "parameters": params,
        })

    _log_step(exec_id, user_id, "action_validation", f"Validated {len(validated_actions)} / {len(proposed)} actions")
    return {"validated_actions": validated_actions}


def node_assess_risk(state: AutomationWorkflowState) -> Dict[str, Any]:
    """Phase 5: Classify aggregate risk level and approval requirement."""
    exec_id = state["execution_id"]
    user_id = state["user_id"]
    actions = state.get("validated_actions", [])

    if not actions:
        risk_level = "low"
        requires_approval = False
    elif any(a.get("risk_level") == "high" for a in actions):
        risk_level = "high"
        requires_approval = True
    elif any(a.get("risk_level") == "medium" for a in actions):
        risk_level = "medium"
        requires_approval = True
    else:
        risk_level = "low"
        requires_approval = False

    _log_step(exec_id, user_id, "risk_assessment", f"Risk level assessed as '{risk_level}' (Approval required: {requires_approval})")
    return {
        "risk_level": risk_level,
        "requires_approval": requires_approval,
    }


def node_approval_gate(state: AutomationWorkflowState) -> Dict[str, Any]:
    """Phase 6: Gate execution and persist approval records for medium/high risk actions."""
    exec_id = state["execution_id"]
    user_id = state["user_id"]
    actions = state.get("validated_actions", [])
    requires_approval = state.get("requires_approval", False)

    approvals_created = []

    # Persist actions in DB
    db_actions = []
    for a in actions:
        param_json = json.dumps(a["parameters"], sort_keys=True)
        param_hash = hashlib.sha256(param_json.encode("utf-8")).hexdigest()

        action_record = AutomationAction(
            execution_id=exec_id,
            user_id=user_id,
            sequence_order=a["sequence_order"],
            tool_name=a["tool_name"],
            action_type=a["action_type"],
            description=a["description"],
            risk_level=a["risk_level"],
            requires_approval=a["requires_approval"],
            parameters=a["parameters"],
            status="awaiting_approval" if a["requires_approval"] else "pending",
        )
        db.session.add(action_record)
        db.session.flush()

        if a["requires_approval"]:
            approval_record = AutomationApproval(
                execution_id=exec_id,
                action_id=action_record.id,
                user_id=user_id,
                status="pending",
                parameter_hash=param_hash,
                change_summary=f"Propose {a['action_type']}: {a['description']}",
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
            )
            db.session.add(approval_record)
            approvals_created.append(approval_record.to_dict())

        db_actions.append(action_record)

    db.session.commit()

    new_status = "awaiting_approval" if requires_approval else "executing"
    _log_step(exec_id, user_id, "approval_gate", f"Approval gate set status to '{new_status}' with {len(approvals_created)} approval(s)")

    return {
        "status": new_status,
        "approvals_created": approvals_created,
    }


def node_execute_actions(state: AutomationWorkflowState) -> Dict[str, Any]:
    """Phase 7: Execute low-risk autonomous actions immediately."""
    exec_id = state["execution_id"]
    user_id = state["user_id"]
    status = state.get("status")

    executed_results = []

    # If execution is awaiting approval, stop before mutating records
    if status == "awaiting_approval":
        return {
            "status": "awaiting_approval",
            "executed_results": []
        }

    # Fetch actions ready to execute
    actions = AutomationAction.query.filter_by(execution_id=exec_id, user_id=user_id).all()
    for act in actions:
        if act.status == "pending" and not act.requires_approval:
            try:
                result = automation_tool_registry.execute_tool(
                    act.tool_name,
                    user_id,
                    act.parameters
                )
                act.status = "executed"
                act.result_payload = result
                executed_results.append(result)
            except Exception as e:
                act.status = "failed"
                act.error_message = str(e)
                _log_step(exec_id, user_id, "execution", f"Action {act.id} failed: {str(e)}", level="error")

    db.session.commit()
    _log_step(exec_id, user_id, "execution", f"Executed {len(executed_results)} low-risk action(s)")

    return {
        "status": "completed",
        "executed_results": executed_results,
    }


def node_verify_results(state: AutomationWorkflowState) -> Dict[str, Any]:
    """Phase 8: Verify execution output and state integrity."""
    exec_id = state["execution_id"]
    user_id = state["user_id"]
    status = state.get("status")

    if status == "awaiting_approval":
        _log_step(exec_id, user_id, "verification", "Workflow paused at approval gate; awaiting user review")
        return {"verification_passed": True}

    actions = AutomationAction.query.filter_by(execution_id=exec_id, user_id=user_id).all()
    failed = any(a.status == "failed" for a in actions)

    _log_step(exec_id, user_id, "verification", f"Verification complete. Any failures: {failed}")
    return {"verification_passed": not failed}


def node_generate_response(state: AutomationWorkflowState) -> Dict[str, Any]:
    """Phase 9: Synthesize final user-facing response with clear action status."""
    narrative = state.get("final_response", "")
    approvals = state.get("approvals_created", [])
    executed = state.get("executed_results", [])

    addendum = ""
    if approvals:
        addendum += f"\n\n⚡ **Pending Approvals ({len(approvals)})**:\n"
        for ap in approvals:
            addendum += f"- {ap.get('change_summary', 'Action requires approval')}\n"
        addendum += "\n*Review and approve these actions in the Automations tab to execute them.*"
    elif executed:
        addendum += f"\n\n✅ *{len(executed)} autonomous action(s) executed successfully.*"

    full_response = narrative + addendum
    return {"final_response": full_response}


# -----------------------------------------------------------------------------
# Graph Construction & Compilation
# -----------------------------------------------------------------------------

def build_automation_graph():
    """Compile and return the executable LangGraph Automation StateGraph."""
    builder = StateGraph(AutomationWorkflowState)

    builder.add_node("classify_intent", node_classify_intent)
    builder.add_node("retrieve_context", node_retrieve_context)
    builder.add_node("plan_automation", node_plan_automation)
    builder.add_node("validate_actions", node_validate_actions)
    builder.add_node("assess_risk", node_assess_risk)
    builder.add_node("approval_gate", node_approval_gate)
    builder.add_node("execute_actions", node_execute_actions)
    builder.add_node("verify_results", node_verify_results)
    builder.add_node("generate_response", node_generate_response)

    # Linear and conditional workflow edges
    builder.add_edge(START, "classify_intent")
    builder.add_edge("classify_intent", "retrieve_context")
    builder.add_edge("retrieve_context", "plan_automation")
    builder.add_edge("plan_automation", "validate_actions")
    builder.add_edge("validate_actions", "assess_risk")
    builder.add_edge("assess_risk", "approval_gate")
    builder.add_edge("approval_gate", "execute_actions")
    builder.add_edge("execute_actions", "verify_results")
    builder.add_edge("verify_results", "generate_response")
    builder.add_edge("generate_response", END)

    return builder.compile()


lifeos_automation_graph = build_automation_graph()
