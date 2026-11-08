import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useTheme } from '../../theme';
import { useApproveAction, useRejectAction } from '../../hooks/useAutomations';
import { AutomationApproval } from '../../types/automation';

export const AutomationApprovalScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const { approval } = (route.params || {}) as { approval: AutomationApproval };

  const approveMutation = useApproveAction();
  const rejectMutation = useRejectAction();

  if (!approval) {
    return (
      <View style={[styles.container, styles.center, { backgroundColor: theme.colors.background }]}>
        <Text style={{ color: theme.colors.textPrimary }}>No approval specified</Text>
      </View>
    );
  }

  const handleApprove = async () => {
    await approveMutation.mutateAsync(approval.id);
    navigation.goBack();
  };

  const handleReject = async () => {
    await rejectMutation.mutateAsync({ approvalId: approval.id });
    navigation.goBack();
  };

  const action = approval.action_summary;

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={[styles.header, { borderBottomColor: theme.colors.border }]}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="close" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: theme.colors.textPrimary }]}>Action Approval Gate</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={[styles.card, { backgroundColor: '#FFFFFF', borderColor: theme.colors.border }]}>
          <View style={styles.riskBadge}>
            <Ionicons name="shield-checkmark" size={16} color="#D97706" />
            <Text style={styles.riskText}>REQUIRES USER CONFIRMATION</Text>
          </View>

          <Text style={[styles.summaryTitle, { color: theme.colors.textPrimary }]}>Proposed Action</Text>
          <Text style={[styles.summaryDesc, { color: theme.colors.textSecondary }]}>
            {approval.change_summary}
          </Text>

          {action ? (
            <View style={styles.paramsBox}>
              <Text style={styles.paramsTitle}>Parameters:</Text>
              <Text style={styles.paramsCode}>
                {JSON.stringify(action.parameters, null, 2)}
              </Text>
            </View>
          ) : null}

          <View style={styles.warningBox}>
            <Ionicons name="information-circle-outline" size={18} color="#2563EB" />
            <Text style={styles.warningText}>
              Review the exact parameters above. Approval directly authorizes this action in your LifeOS database.
            </Text>
          </View>
        </View>

        <View style={styles.actionRow}>
          <TouchableOpacity
            style={[styles.rejectBtn, { borderColor: '#EF4444' }]}
            onPress={handleReject}
            disabled={rejectMutation.isPending || approveMutation.isPending}
          >
            {rejectMutation.isPending ? (
              <ActivityIndicator size="small" color="#EF4444" />
            ) : (
              <Text style={styles.rejectBtnText}>Reject</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.approveBtn, { backgroundColor: '#10B981' }]}
            onPress={handleApprove}
            disabled={rejectMutation.isPending || approveMutation.isPending}
          >
            {approveMutation.isPending ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Text style={styles.approveBtnText}>Approve & Execute</Text>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  center: {
    justifyContent: 'center',
    alignItems: 'center',
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
  card: {
    borderRadius: 16,
    borderWidth: 1,
    padding: 18,
  },
  riskBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: '#FEF3C7',
    alignSelf: 'flex-start',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
    marginBottom: 12,
  },
  riskText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#D97706',
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 6,
  },
  summaryDesc: {
    fontSize: 14,
    lineHeight: 20,
  },
  paramsBox: {
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
    padding: 12,
    marginTop: 14,
  },
  paramsTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6B7280',
    marginBottom: 4,
  },
  paramsCode: {
    fontFamily: 'monospace',
    fontSize: 12,
    color: '#374151',
  },
  warningBox: {
    flexDirection: 'row',
    gap: 8,
    backgroundColor: '#EFF6FF',
    borderRadius: 10,
    padding: 12,
    marginTop: 16,
    alignItems: 'center',
  },
  warningText: {
    fontSize: 12,
    color: '#1E40AF',
    flex: 1,
    lineHeight: 16,
  },
  actionRow: {
    flexDirection: 'row',
    gap: 12,
  },
  rejectBtn: {
    flex: 1,
    borderWidth: 1.5,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  rejectBtnText: {
    color: '#EF4444',
    fontSize: 15,
    fontWeight: '600',
  },
  approveBtn: {
    flex: 2,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  approveBtnText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '600',
  },
});
