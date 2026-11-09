import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';
import { ImprovementDashboardData } from '../../types/aiImprovement';

export const AIImprovementDashboardScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const { data, isLoading, error, refetch } = useQuery<ImprovementDashboardData>({
    queryKey: ['ai-improvement-dashboard'],
    queryFn: async () => {
      const resp = await apiClient.get('/api/v1/ai/improvement/dashboard');
      return resp.data.data;
    },
  });

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backButtonText}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>AI Model Pipeline</Text>
        <TouchableOpacity onPress={() => refetch()} style={styles.refreshButton}>
          <Text style={styles.refreshButtonText}>Refresh</Text>
        </TouchableOpacity>
      </View>

      {isLoading ? (
        <View style={styles.centered}>
          <ActivityIndicator size="large" color="#4F46E5" />
          <Text style={styles.loadingText}>Loading AI Improvement Telemetry...</Text>
        </View>
      ) : error ? (
        <View style={styles.centered}>
          <Text style={styles.errorText}>Unable to load improvement metrics.</Text>
          <TouchableOpacity onPress={() => refetch()} style={styles.retryButton}>
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <ScrollView style={styles.content}>
          {/* Active Runtime Model Card */}
          <View style={styles.card}>
            <Text style={styles.cardLabel}>ACTIVE PRODUCTION MODEL</Text>
            <Text style={styles.modelTag}>{data?.active_runtime_model?.model_tag || 'qwen2.5:3b'}</Text>
            <View style={styles.badgeRow}>
              <View style={[styles.badge, styles.badgeActive]}>
                <Text style={styles.badgeText}>Active Runtime</Text>
              </View>
              {data?.active_runtime_model?.evaluation_score ? (
                <View style={[styles.badge, styles.badgeScore]}>
                  <Text style={styles.badgeText}>
                    Benchmark: {(data.active_runtime_model.evaluation_score * 100).toFixed(1)}%
                  </Text>
                </View>
              ) : null}
            </View>
          </View>

          {/* Feedback & Dataset Readiness Overview */}
          <View style={styles.statsRow}>
            <View style={[styles.statBox, { marginRight: 8 }]}>
              <Text style={styles.statNumber}>{data?.feedback_summary?.total_feedback || 0}</Text>
              <Text style={styles.statLabel}>User Feedbacks</Text>
              <Text style={styles.statSub}>
                +{data?.feedback_summary?.positive || 0} / -{data?.feedback_summary?.negative || 0}
              </Text>
            </View>
            <View style={[styles.statBox, { marginLeft: 8 }]}>
              <Text style={styles.statNumber}>{data?.dataset_versions_count || 0}</Text>
              <Text style={styles.statLabel}>Dataset Snapshots</Text>
              <Text style={styles.statSub}>Curated for LoRA</Text>
            </View>
          </View>

          {/* Training Jobs Summary */}
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Training Job Orchestration</Text>
          </View>

          {data?.training_jobs && data.training_jobs.length > 0 ? (
            data.training_jobs.map((job) => (
              <View key={job.id} style={styles.jobItem}>
                <View style={styles.jobHeader}>
                  <Text style={styles.jobName}>{job.job_name}</Text>
                  <View style={[
                    styles.statusPill,
                    job.status === 'completed'
                      ? styles.statusSuccess
                      : job.status === 'dry_run_validated'
                      ? styles.statusDryRun
                      : styles.statusPending
                  ]}>
                    <Text style={styles.statusPillText}>
                      {job.status === 'dry_run_validated' ? 'DRY-RUN VALIDATED' : job.status.toUpperCase()}
                    </Text>
                  </View>
                </View>
                <Text style={styles.jobMeta}>Candidate: {job.candidate_model_tag}</Text>
                <Text style={styles.jobDate}>{new Date(job.created_at).toLocaleDateString()}</Text>
              </View>
            ))
          ) : (
            <View style={styles.emptyCard}>
              <Text style={styles.emptyText}>No training jobs orchestrated yet.</Text>
            </View>
          )}

          {/* Registered Candidate Models */}
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Model Registry & Candidates</Text>
          </View>

          {data?.registered_models && data.registered_models.length > 0 ? (
            data.registered_models.map((model) => (
              <View key={model.id} style={styles.modelItem}>
                <View style={styles.modelItemHeader}>
                  <Text style={styles.modelItemTag}>{model.model_tag}</Text>
                  {model.is_active && (
                    <View style={[styles.badge, styles.badgeActive]}>
                      <Text style={styles.badgeText}>Active</Text>
                    </View>
                  )}
                </View>
                <Text style={styles.modelVersion}>Version: {model.version_tag} • Status: {model.status}</Text>
                {model.evaluation_score !== null && model.evaluation_score !== undefined && (
                  <Text style={styles.modelEval}>
                    STEP 9 Benchmark Score: {(model.evaluation_score * 100).toFixed(1)}%
                  </Text>
                )}
              </View>
            ))
          ) : (
            <View style={styles.emptyCard}>
              <Text style={styles.emptyText}>No candidate models registered.</Text>
            </View>
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#1E293B',
  },
  backButton: {
    padding: 8,
  },
  backButtonText: {
    color: '#F8FAFC',
    fontSize: 20,
    fontWeight: 'bold',
  },
  headerTitle: {
    color: '#F8FAFC',
    fontSize: 18,
    fontWeight: 'bold',
  },
  refreshButton: {
    padding: 8,
  },
  refreshButtonText: {
    color: '#818CF8',
    fontSize: 14,
    fontWeight: '600',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  loadingText: {
    color: '#94A3B8',
    marginTop: 12,
    fontSize: 14,
  },
  errorText: {
    color: '#EF4444',
    fontSize: 14,
    marginBottom: 12,
  },
  retryButton: {
    backgroundColor: '#4F46E5',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  card: {
    backgroundColor: '#1E293B',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#334155',
  },
  cardLabel: {
    color: '#94A3B8',
    fontSize: 11,
    fontWeight: 'bold',
    letterSpacing: 1,
    marginBottom: 6,
  },
  modelTag: {
    color: '#F8FAFC',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  badgeRow: {
    flexDirection: 'row',
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
    marginRight: 8,
  },
  badgeActive: {
    backgroundColor: '#059669',
  },
  badgeScore: {
    backgroundColor: '#4F46E5',
  },
  badgeText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  statsRow: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  statBox: {
    flex: 1,
    backgroundColor: '#1E293B',
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: '#334155',
  },
  statNumber: {
    color: '#F8FAFC',
    fontSize: 22,
    fontWeight: 'bold',
  },
  statLabel: {
    color: '#94A3B8',
    fontSize: 12,
    marginTop: 4,
  },
  statSub: {
    color: '#64748B',
    fontSize: 11,
    marginTop: 2,
  },
  sectionHeader: {
    marginBottom: 10,
  },
  sectionTitle: {
    color: '#F8FAFC',
    fontSize: 16,
    fontWeight: 'bold',
  },
  jobItem: {
    backgroundColor: '#1E293B',
    borderRadius: 10,
    padding: 14,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#6366F1',
  },
  jobHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  jobName: {
    color: '#F8FAFC',
    fontSize: 15,
    fontWeight: '600',
  },
  statusPill: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  statusSuccess: {
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
  },
  statusDryRun: {
    backgroundColor: 'rgba(234, 179, 8, 0.2)',
  },
  statusPending: {
    backgroundColor: 'rgba(99, 102, 241, 0.2)',
  },
  statusPillText: {
    color: '#A5B4FC',
    fontSize: 10,
    fontWeight: '700',
  },
  jobMeta: {
    color: '#94A3B8',
    fontSize: 13,
  },
  jobDate: {
    color: '#64748B',
    fontSize: 11,
    marginTop: 4,
  },
  modelItem: {
    backgroundColor: '#1E293B',
    borderRadius: 10,
    padding: 14,
    marginBottom: 10,
  },
  modelItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  modelItemTag: {
    color: '#F8FAFC',
    fontSize: 15,
    fontWeight: '600',
  },
  modelVersion: {
    color: '#94A3B8',
    fontSize: 13,
    marginBottom: 4,
  },
  modelEval: {
    color: '#34D399',
    fontSize: 12,
    fontWeight: '500',
  },
  emptyCard: {
    backgroundColor: '#1E293B',
    borderRadius: 10,
    padding: 16,
    alignItems: 'center',
    marginBottom: 16,
  },
  emptyText: {
    color: '#64748B',
    fontSize: 13,
  },
});

