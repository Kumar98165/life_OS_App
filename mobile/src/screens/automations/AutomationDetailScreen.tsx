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
import { useAutomationDetail, useExecuteAutomation } from '../../hooks/useAutomations';

export const AutomationDetailScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const { id } = route.params || {};

  const { data: item, isLoading } = useAutomationDetail(id);
  const executeMutation = useExecuteAutomation();

  if (isLoading || !item) {
    return (
      <View style={[styles.container, styles.center, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  const handleRunNow = async () => {
    try {
      const exec = await executeMutation.mutateAsync({ id: item.id });
      navigation.navigate('AutomationExecutionHistory', { executionId: exec.id });
    } catch (e) {
      //
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={[styles.header, { borderBottomColor: theme.colors.border }]}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: theme.colors.textPrimary }]} numberOfLines={1}>
          {item.title}
        </Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={[styles.card, { backgroundColor: '#FFFFFF', borderColor: theme.colors.border }]}>
          <View style={[styles.badge, { backgroundColor: `${theme.colors.primary}15` }]}>
            <Text style={[styles.badgeText, { color: theme.colors.primary }]}>
              {item.category.toUpperCase()}
            </Text>
          </View>
          <Text style={[styles.title, { color: theme.colors.textPrimary }]}>{item.title}</Text>
          <Text style={[styles.desc, { color: theme.colors.textSecondary }]}>
            {item.description || 'No description provided.'}
          </Text>

          <View style={styles.statGrid}>
            <View style={styles.statBox}>
              <Text style={[styles.statNum, { color: theme.colors.textPrimary }]}>{item.total_runs}</Text>
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>Total Runs</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={[styles.statNum, { color: '#10B981' }]}>{item.successful_runs}</Text>
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>Successful</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={[styles.statNum, { color: item.failed_runs > 0 ? '#EF4444' : theme.colors.textPrimary }]}>
                {item.failed_runs}
              </Text>
              <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>Failed</Text>
            </View>
          </View>
        </View>

        <View style={[styles.card, { backgroundColor: '#FFFFFF', borderColor: theme.colors.border }]}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Trigger Configuration</Text>
          <View style={styles.infoRow}>
            <Text style={[styles.infoLabel, { color: theme.colors.textSecondary }]}>Trigger Type:</Text>
            <Text style={[styles.infoVal, { color: theme.colors.textPrimary }]}>{item.trigger_type}</Text>
          </View>
          {item.trigger_type === 'scheduled' ? (
            <>
              <View style={styles.infoRow}>
                <Text style={[styles.infoLabel, { color: theme.colors.textSecondary }]}>Time:</Text>
                <Text style={[styles.infoVal, { color: theme.colors.textPrimary }]}>{item.scheduled_time || '08:00'}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={[styles.infoLabel, { color: theme.colors.textSecondary }]}>Days:</Text>
                <Text style={[styles.infoVal, { color: theme.colors.textPrimary }]}>{item.scheduled_days || 'Daily'}</Text>
              </View>
            </>
          ) : null}
          <View style={styles.infoRow}>
            <Text style={[styles.infoLabel, { color: theme.colors.textSecondary }]}>Status:</Text>
            <Text style={[styles.infoVal, { color: item.is_paused ? '#F59E0B' : '#10B981' }]}>
              {item.is_paused ? 'Paused' : 'Active'}
            </Text>
          </View>
        </View>

        <TouchableOpacity
          style={[styles.primaryRunBtn, { backgroundColor: theme.colors.primary }]}
          onPress={handleRunNow}
          disabled={executeMutation.isPending}
        >
          {executeMutation.isPending ? (
            <ActivityIndicator size="small" color="#FFFFFF" />
          ) : (
            <>
              <Ionicons name="flash" size={16} color="#FFFFFF" />
              <Text style={styles.primaryRunBtnText}>Execute Automation</Text>
            </>
          )}
        </TouchableOpacity>
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
    flex: 1,
  },
  content: {
    padding: 16,
    gap: 14,
  },
  card: {
    borderRadius: 16,
    borderWidth: 1,
    padding: 18,
  },
  badge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    marginBottom: 8,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '700',
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 6,
  },
  desc: {
    fontSize: 14,
    lineHeight: 20,
  },
  statGrid: {
    flexDirection: 'row',
    marginTop: 18,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#E5E7EB',
    paddingTop: 14,
  },
  statBox: {
    flex: 1,
    alignItems: 'center',
  },
  statNum: {
    fontSize: 18,
    fontWeight: '700',
  },
  statLabel: {
    fontSize: 11,
    marginTop: 2,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
  },
  infoLabel: {
    fontSize: 13,
  },
  infoVal: {
    fontSize: 13,
    fontWeight: '600',
  },
  primaryRunBtn: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
    paddingVertical: 14,
    borderRadius: 12,
    marginTop: 10,
  },
  primaryRunBtnText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '600',
  },
});
