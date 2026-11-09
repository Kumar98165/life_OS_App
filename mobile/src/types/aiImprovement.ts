export interface ImprovementDashboardData {
  active_runtime_model: {
    model_tag: string;
    version_tag?: string;
    status?: string;
    evaluation_score?: number | null;
  };
  feedback_summary: {
    total_feedback: number;
    positive: number;
    negative: number;
  };
  dataset_versions_count: number;
  latest_dataset_versions: Array<{
    id: string;
    version_name: string;
    sample_count: number;
    manifest_hash: string;
    created_at: string;
  }>;
  training_jobs: Array<{
    id: string;
    job_name: string;
    candidate_model_tag: string;
    status: 'pending' | 'validating' | 'ready' | 'running' | 'completed' | 'failed' | 'cancelled';
    created_at: string;
  }>;
  model_versions_count: number;
  registered_models: Array<{
    id: string;
    model_tag: string;
    version_tag: string;
    status: string;
    is_active: boolean;
    evaluation_score?: number | null;
  }>;
  timestamp: string;
}

export interface DatasetReadinessReport {
  dataset_version_id: string;
  version_name: string;
  total_samples: number;
  minimum_required_samples: number;
  valid_samples_count: number;
  sanitized_samples_count: number;
  consented_samples_count: number;
  approved_samples_count: number;
  duplicate_count: number;
  duplicate_rate: number;
  average_quality_score: number;
  is_ready_for_training: boolean;
  blocking_reasons: string[];
  evaluated_at: string;
}

