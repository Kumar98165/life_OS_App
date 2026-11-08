/**
 * LifeOS - Automation API Client Types.
 */

export interface AutomationDefinition {
  id: string;
  user_id: string | null;
  slug: string;
  title: string;
  description?: string;
  category: 'productivity' | 'review' | 'health' | 'finance';
  is_template: boolean;
  is_active: boolean;
  is_paused: boolean;
  trigger_type: 'manual' | 'scheduled' | 'event';
  cron_expression?: string;
  scheduled_time?: string;
  scheduled_days?: string;
  configuration: Record<string, any>;
  last_run_at?: string;
  next_run_at?: string;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  created_at: string;
}

export interface AutomationTemplate {
  slug: string;
  title: string;
  category: 'productivity' | 'review' | 'health' | 'finance';
  description: string;
  trigger_type: 'manual' | 'scheduled' | 'event';
  scheduled_time?: string;
  scheduled_days?: string;
  configuration: Record<string, any>;
}

export interface AutomationAction {
  id: string;
  execution_id: string;
  user_id: string;
  sequence_order: number;
  tool_name: string;
  action_type: string;
  description: string;
  risk_level: 'low' | 'medium' | 'high';
  requires_approval: boolean;
  parameters: Record<string, any>;
  result_payload?: Record<string, any>;
  status: 'pending' | 'awaiting_approval' | 'approved' | 'rejected' | 'executed' | 'failed' | 'skipped';
  error_message?: string;
  has_approval: boolean;
  approval_id?: string;
  created_at: string;
}

export interface AutomationApproval {
  id: string;
  execution_id: string;
  action_id: string;
  user_id: string;
  status: 'pending' | 'approved' | 'rejected' | 'expired' | 'cancelled';
  parameter_hash: string;
  change_summary: string;
  expires_at: string;
  responded_at?: string;
  decision_reason?: string;
  is_expired: boolean;
  action_summary?: {
    tool_name: string;
    action_type: string;
    description: string;
    risk_level: string;
    parameters: Record<string, any>;
  };
  created_at: string;
}

export interface AutomationExecutionLog {
  id: string;
  execution_id: string;
  step_name: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  details?: Record<string, any>;
  created_at: string;
}

export interface AutomationExecution {
  id: string;
  user_id: string;
  definition_id?: string;
  definition_title?: string;
  definition_slug?: string;
  idempotency_key?: string;
  triggered_by: 'manual' | 'scheduled' | 'assistant_prompt';
  status: 'pending' | 'planning' | 'awaiting_approval' | 'executing' | 'completed' | 'failed' | 'cancelled' | 'paused';
  risk_level: 'low' | 'medium' | 'high';
  trigger_payload: Record<string, any>;
  summary?: string;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  execution_duration_ms?: number;
  retry_count: number;
  max_retries: number;
  created_at: string;
  actions?: AutomationAction[];
  approvals?: AutomationApproval[];
  logs?: AutomationExecutionLog[];
}
