import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  FlatList,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useTheme } from '../../theme';
import { useAutomationExecutions, useExecutionDetail, useCancelExecution } from '../../hooks/useAutomations';
import { AutomationExecution } from '../../types/automation';

export const AutomationExecutionHistoryScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const { executionId } = route.params || {};

  const { data: executions = [], isLoading } = useAutomationExecutions();
  const { data: selectedExecution } = useExecutionDetail(executionId || '');
  const cancelMutation = useCancelExecution();

  const activeItem: AutomationExecution | undefined = selectedExecution || executions[0];

  const renderStatusBadge = (status: string) => {
    let color = '#6B7280';
    let bg = '#F3F4F6';
    if (status === 'completed') {
      color = '#10B981';
      bg = '#D1FAE5';
    } else if (status === 'awaiting_approval') {
      color = '#D97706';
      bg = '#FEF3C7';
    } else if (status === 'failed') {
      color = '#EF4444';
      bg = '#FEE2E2';
    } else if (status === 'executing' || status === 'planning') {
      color = '#2563EB';
      bg = '#DBEAFE';
    }

    return (
      <View style={[styles.statusBadge, { backgroundColor: bg }]}>
        <Text style={[styles.statusText, { color }]}>{status.replace('_', ' ').toUpperCase()}</Text>
      </View>
    );
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={[styles.header, { borderBottomColor: theme.colors.border }]}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: theme.colors.textPrimary }]}>Execution History</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {activeItem ? (
          <View style={[styles.activeCard, { backgroundColor: '#FFFFFF', borderColor: theme.colors.border }]}>
            <View style={styles.cardTop}>
              <Text style={[styles.defTitle, { color: theme.colors.textPrimary }]}>
                {activeItem.definition_title || 'Automation Run'}
              </Text>
              {renderStatusBadge(activeItem.status)}
            </View>

            {activeItem.summary ? (
              <View style={styles.summaryBox}>
                <Text style={styles.summaryLabel}>Response & Plan:</Text>
                <Text style={styles.summaryText}>{activeItem.summary}</Text>
              </View>
            ) : null}

            {activeItem.approvals && activeItem.approvals.length > 0 ? (
              <View style={styles.approvalsSection}>
                <Text style={styles.sectionTitle}>
                  Pending Action Approvals ({activeItem.approvals.filter(a => a.status === 'pending').length})
                </Text>
                {activeItem.approvals.map((ap) => (
                  <TouchableOpacity
                    key={ap.id}
                    style={styles.approvalItem}
                    onPress={() => navigation.navigate('AutomationApproval', { approval: ap })}
                  >
                    <View style={styles.approvalLeft}>
                      <Ionicons name="shield-outline" size={18} color="#D97706" />
                      <Text style={styles.approvalDesc} numberOfLines={2}>
                        {ap.change_summary}
                      </Text>
                    </View>
                    <Ionicons name="chevron-forward" size={16} color="#9CA3AF" />
                  </TouchableOpacity>
                ))}
              </View>
            ) : null}

            {activeItem.status === 'awaiting_approval' ? (
              <TouchableOpacity
                style={styles.cancelBtn}
                onPress={() => cancelMutation.mutate(activeItem.id)}
              >
                <Text style={styles.cancelBtnText}>Cancel Execution</Text>
              </TouchableOpacity>
            ) : null}
          </View>
        ) : null}

        <Text style={[styles.historyHeading, { color: theme.colors.textPrimary }]}>Recent Executions</Text>

        {executions.map((item) => (
          <TouchableOpacity
            key={item.id}
            style={[styles.historyRow, { backgroundColor: '#FFFFFF', borderColor: theme.colors.border }]}
            onPress={() => navigation.setParams({ executionId: item.id })}
          >
            <View style={styles.rowLeft}>
              <Text style={[styles.rowTitle, { color: theme.colors.textPrimary }]}>
                {item.definition_title || 'Execution'}
              </Text>
              <Text style={[styles.rowDate, { color: theme.colors.textSecondary }]}>
                {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </Text>
            </View>
            {renderStatusBadge(item.status)}
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    gap: 12,
  },
  backBtn: {
    padding: 4,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  content: {
    padding: 16,
    gap: 16,
  },
  activeCard: {
    borderRadius: 16,
    borderWidth: 1,
    padding: 16,
  },
  cardTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  defTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '700',
  },
  summaryBox: {
    backgroundColor: '#F9FAFB',
    borderRadius: 10,
    padding: 12,
    marginTop: 8,
  },
  summaryLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#6B7280',
    marginBottom: 4,
  },
  summaryText: {
    fontSize: 13,
    lineHeight: 18,
    color: '#374151',
  },
  approvalsSection: {
    marginTop: 16,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#E5E7EB',
    paddingTop: 12,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#111827',
  },
  approvalItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#FFFBEB',
    borderWidth: 1,
    borderColor: '#FDE68A',
    borderRadius: 8,
    padding: 10,
    marginBottom: 8,
  },
  approvalLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    flex: 1,
  },
  approvalDesc: {
    fontSize: 12,
    color: '#92400E',
    fontWeight: '500',
    flex: 1,
  },
  cancelBtn: {
    marginTop: 12,
    paddingVertical: 10,
    alignItems: 'center',
  },
  cancelBtnText: {
    color: '#EF4444',
    fontSize: 13,
    fontWeight: '600',
  },
  historyHeading: {
    fontSize: 16,
    fontWeight: '700',
    marginTop: 8,
  },
  historyRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
  },
  rowLeft: {
    gap: 2,
  },
  rowTitle: {
    fontSize: 14,
    fontWeight: '600',
  },
  rowDate: {
    fontSize: 12,
  },
});
